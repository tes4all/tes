import json
import click
import boto3
import datetime
import sys
from botocore.exceptions import ClientError, NoCredentialsError

@click.group()
def route53():
    """Route53 commands."""
    pass


def _to_bind(zone_name, records):
    lines = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"; Domain: {zone_name}")
    lines.append(f"; Exported (y-m-d hh:mm:ss): {now}")
    lines.append("; Actual version")
    lines.append("")

    c_zone_name = zone_name.rstrip(".") + "."

    def format_name(record_name):
        if record_name == c_zone_name:
            return "@"
        if record_name.endswith("." + c_zone_name):
             return record_name[: -(len(c_zone_name) + 1)]
        return record_name

    soa_record = next((r for r in records if r["Type"] == "SOA"), None)
    if soa_record:
        default_ttl = soa_record.get("TTL", 3600)
        lines.append(f"$TTL {default_ttl}")

    def format_records(recs):
        processed_cnames = set()
        for r in recs:
            name = format_name(r["Name"])
            ttl = r.get("TTL", "")
            r_type = r["Type"]

            if "ResourceRecords" in r:
                for rr in r["ResourceRecords"]:
                    value = rr["Value"]
                    lines.append(f"{name:<20} {ttl:<5} IN {r_type:<4} {value}")
            elif "AliasTarget" in r:
                alias = r["AliasTarget"]
                if name in processed_cnames:
                    lines.append(f"; Skipped duplicate ALIAS/CNAME for {name}")
                    continue
                processed_cnames.add(name)
                lines.append(f"; ALIAS record to {alias['DNSName']}")
                lines.append(f"{name:<20} {ttl:<5} IN CNAME {alias['DNSName']}")

    # Order: SOA, NS, others
    if soa_record:
        format_records([soa_record])

    ns_records = [r for r in records if r["Type"] == "NS"]
    format_records(ns_records)

    other_records = [r for r in records if r["Type"] not in ("SOA", "NS")]
    other_records.sort(key=lambda x: x["Name"])
    format_records(other_records)

    return "\n".join(lines)


@route53.command()
@click.option("--id", help="The hosted zone ID.")
@click.option("--name", help="The hosted zone name.")
@click.option("--output", "-o", type=click.File("w"), default="-", help="Output file. Defaults to print to stdout.")
@click.option("--format", "-f", type=click.Choice(["json", "bind"], case_sensitive=False), default="json", help="Output format (json or bind). Default is json.")
def export(id, name, output, format):
    """Export a Route53 DNS zone to JSON or BIND format."""
    if not id and not name:
        raise click.UsageError("Either --id or --name must be provided.")
    try:
        client = boto3.client("route53")

        if not id:
            # Resolve name to id
            response = client.list_hosted_zones_by_name(DNSName=name)
            target_name = name.rstrip(".") + "."

            # list_hosted_zones_by_name starts listing FROM the name, but doesn't guarantee equality
            found = False
            for zone in response.get("HostedZones", []):
                if zone["Name"] == target_name:
                    id = zone["Id"]
                    found = True
                    break

            if not found:
                 raise click.UsageError(f"Hosted zone '{name}' not found.")

        # If we need name for BIND but only have ID
        if not name and format == "bind":
             z_info = client.get_hosted_zone(Id=id)
             name = z_info["HostedZone"]["Name"]

        paginator = client.get_paginator("list_resource_record_sets")

        records = []
        for page in paginator.paginate(HostedZoneId=id):
            records.extend(page.get("ResourceRecordSets", []))

        if format == "json":
            json.dump(records, output, indent=2, default=str)
            output.write("\n")
        else:
            bind_content = _to_bind(name, records)
            output.write(bind_content)
            output.write("\n")

    except NoCredentialsError:
        click.echo("Error: No AWS credentials found.", err=True)
    except ClientError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
