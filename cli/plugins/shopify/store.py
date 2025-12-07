"""Shopify store management commands.

This module exposes higher level workflows around cloning data between stores and
seeding rich test data into a development environment. The implementation is
designed to stay within the public Admin API surface so that it can run from a
developer workstation without additional infrastructure.
"""

from __future__ import annotations

import base64
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import click
import requests


API_VERSION = os.environ.get("TES_SHOPIFY_API_VERSION", "2023-07")
DEFAULT_TIMEOUT = 30
DEFAULT_RATE_LIMIT_SLEEP = 1.5
DEFAULT_PAGE_LIMIT = 250


try:
	from .. import utils
except ImportError:  # pragma: no cover - fallback when executed inside package
	from cli.plugins import utils


class _NullProgressBar:
	def update(self, _=1) -> None:
		return None


class _NullProgressContext:
	def __enter__(self) -> _NullProgressBar:
		return _NullProgressBar()


	def __exit__(self, exc_type, exc, tb) -> bool:
		return False


class ProgressManager:
	def __init__(self, echo_func=None) -> None:
		self._echo = echo_func or (lambda _message: None)

	def announce(self, message: str) -> None:
		self._echo(message)

	def task(
		self,
		name: str,
		*,
		total: Optional[int] = None,
		label: Optional[str] = None,
	):
		return _NullProgressContext()


class ClickProgressManager(ProgressManager):
	def __init__(self, echo_func=None) -> None:
		super().__init__(echo_func or click.echo)

	def task(
		self,
		name: str,
		*,
		total: Optional[int] = None,
		label: Optional[str] = None,
	):
		if total in (None, 0):
			return _NullProgressContext()
		return click.progressbar(length=total, label=label or name.title())


class ShopifyAPIError(RuntimeError):
	"""Raised when the Shopify Admin API reports an error."""


def _slugify(value: str) -> str:
	cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
	return cleaned or "item"


def _safe_get(mapping: Dict, *path, default=None):
	current = mapping
	for key in path:
		if not isinstance(current, dict) or key not in current:
			return default
		current = current[key]
	return current


class ShopifyAdminAPI:
	"""Minimal REST + GraphQL helper around the Shopify Admin API."""

	def __init__(
		self,
		store_domain: str,
		access_token: str,
		*,
		timeout: int = DEFAULT_TIMEOUT,
		rate_limit_sleep: float = DEFAULT_RATE_LIMIT_SLEEP,
		session: Optional[requests.Session] = None,
	) -> None:
		if not store_domain.endswith(".myshopify.com"):
			store_domain = f"{store_domain}.myshopify.com"

		self.store_domain = store_domain
		self.base_url = f"https://{store_domain}/admin/api/{API_VERSION}"
		self.graphql_url = f"https://{store_domain}/admin/api/{API_VERSION}/graphql.json"
		self.timeout = timeout
		self.rate_limit_sleep = rate_limit_sleep
		self.session = session or requests.Session()
		self.session.headers.update(
			{
				"X-Shopify-Access-Token": access_token,
				"Accept": "application/json",
				"Content-Type": "application/json",
			}
		)

	# ------------------------------------------------------------------
	# Low level request helpers
	# ------------------------------------------------------------------

	def _request(
		self,
		method: str,
		path: str,
		*,
		params: Optional[Dict] = None,
		payload: Optional[Dict] = None,
		stream: bool = False,
		retries: int = 3,
	) -> requests.Response:
		url = path if path.startswith("http") else f"{self.base_url}{path}"

		for attempt in range(1, retries + 1):
			response = self.session.request(
				method,
				url,
				params=params,
				json=payload,
				timeout=self.timeout,
				stream=stream,
			)

			if response.status_code == 429:
				retry_after = float(response.headers.get("Retry-After", self.rate_limit_sleep))
				time.sleep(retry_after)
				continue

			if 500 <= response.status_code < 600 and attempt < retries:
				time.sleep(self.rate_limit_sleep)
				continue

			if response.status_code >= 400:
				try:
					details = response.json()
				except ValueError:
					details = response.text
				raise ShopifyAPIError(
					f"Shopify API error ({response.status_code}) for {method} {url}: {details}"
				)

			return response

		raise ShopifyAPIError(f"Shopify API rate limit reached for {method} {url}")

	def _parse_next_link(self, link_header: Optional[str]) -> Optional[str]:
		if not link_header:
			return None

		for part in link_header.split(","):
			segment = part.strip()
			if 'rel="next"' not in segment:
				continue
			start = segment.find("<")
			end = segment.find(">", start)
			if start == -1 or end == -1:
				continue
			return segment[start + 1 : end]
		return None

	def paginate(self, path: str, params: Optional[Dict] = None) -> Iterable[Dict]:
		params = params.copy() if params else {}
		if "limit" not in params:
			params["limit"] = DEFAULT_PAGE_LIMIT

		next_url: Optional[str] = f"{self.base_url}{path}"
		query_params: Optional[Dict] = params

		while next_url:
			response = self._request("GET", next_url, params=query_params)
			yield response.json()
			next_url = self._parse_next_link(response.headers.get("Link"))
			query_params = None

	def graphql(self, query: str, variables: Optional[Dict] = None) -> Dict:
		body = {"query": query, "variables": variables or {}}

		for attempt in range(1, 4):
			response = self.session.post(
				self.graphql_url,
				json=body,
				timeout=self.timeout,
			)

			if response.status_code == 429:
				retry_after = float(response.headers.get("Retry-After", self.rate_limit_sleep))
				time.sleep(retry_after)
				continue

			if response.status_code >= 400:
				raise ShopifyAPIError(
					f"GraphQL request failed ({response.status_code}): {response.text.strip()}"
				)

			payload = response.json()
			if payload.get("errors"):
				raise ShopifyAPIError(f"GraphQL errors: {payload['errors']}")
			if payload.get("data") is None:
				time.sleep(self.rate_limit_sleep)
				continue
			return payload["data"]

		raise ShopifyAPIError("GraphQL request failed after retries")

	# ------------------------------------------------------------------
	# REST helpers for common resources
	# ------------------------------------------------------------------

	def iterate(self, path: str, key: str, params: Optional[Dict] = None) -> Iterable[Dict]:
		for page in self.paginate(path, params=params):
			for item in page.get(key, []):
				yield item

	def product_exists(self, handle: str) -> Optional[int]:
		query = """
		query($handle: String!) {
			productByHandle(handle: $handle) { id legacyResourceId }
		}
		"""
		data = self.graphql(query, {"handle": handle})
		product = _safe_get(data, "productByHandle")
		if not product:
			return None
		legacy_id = product.get("legacyResourceId")
		if legacy_id:
			return int(legacy_id)
		if product.get("id"):
			return int(product["id"].split("/")[-1])
		return None

	def count_products(self) -> int:
		# Try GraphQL first (preferred)
		try:
			data = self.graphql(
				"""
				query ProductsCount { productsCount { count } }
				"""
			)
			value = _safe_get(data, "productsCount", "count")
			if isinstance(value, int):
				return value
			if isinstance(value, str):
				return int(value)
		except (ShopifyAPIError, ValueError, TypeError):
			pass

		# Fallback to REST
		response = self._request("GET", "/products/count.json")
		return int(response.json().get("count", 0))

	def delete_product(self, product_id: int) -> None:
		self._request("DELETE", f"/products/{product_id}.json")

	def create_product(self, product_payload: Dict) -> Dict:
		response = self._request("POST", "/products.json", payload={"product": product_payload})
		return response.json()["product"]

	def list_themes(self) -> List[Dict]:
		response = self._request("GET", "/themes.json")
		return response.json().get("themes", [])

	def list_theme_assets(self, theme_id: int) -> List[Dict]:
		response = self._request("GET", f"/themes/{theme_id}/assets.json")
		return response.json().get("assets", [])

	def get_theme_asset(self, theme_id: int, key: str) -> Dict:
		response = self._request(
			"GET",
			f"/themes/{theme_id}/assets.json",
			params={"asset[key]": key, "theme_id": theme_id},
		)
		return response.json()["asset"]

	def upsert_theme_asset(self, theme_id: int, asset: Dict) -> None:
		payload = {"asset": {"key": asset["key"]}}
		if "value" in asset:
			payload["asset"]["value"] = asset["value"]
		elif "attachment" in asset:
			payload["asset"]["attachment"] = asset["attachment"]
		else:
			payload["asset"]["value"] = ""
		self._request("PUT", f"/themes/{theme_id}/assets.json", payload=payload)

	def create_theme(self, name: str, role: str = "unpublished") -> Dict:
		response = self._request(
			"POST",
			"/themes.json",
			payload={"theme": {"name": name, "role": role}},
		)
		return response.json()["theme"]

	def delete_theme(self, theme_id: int) -> None:
		self._request("DELETE", f"/themes/{theme_id}.json")

	def get_shop(self) -> Dict:
		response = self._request("GET", "/shop.json")
		return response.json()["shop"]

	def iterate_shop_metafields(self) -> Iterable[Dict]:
		shop = self.get_shop()
		params = {
			"metafield[owner_id]": shop["id"],
			"metafield[owner_resource]": "shop",
		}
		return self.iterate("/metafields.json", "metafields", params=params)

	def create_metafield(self, metafield: Dict) -> Dict:
		payload = {"metafield": metafield}
		response = self._request("POST", "/metafields.json", payload=payload)
		return response.json()["metafield"]

	def search_customers(self, query: str) -> List[Dict]:
		response = self._request("GET", "/customers/search.json", params={"query": query})
		return response.json().get("customers", [])

	def create_customer(self, customer_payload: Dict) -> Dict:
		response = self._request("POST", "/customers.json", payload={"customer": customer_payload})
		return response.json()["customer"]

	def create_order(self, order_payload: Dict) -> Dict:
		response = self._request("POST", "/orders.json", payload={"order": order_payload})
		return response.json()["order"]

	def create_price_rule(self, payload: Dict) -> Dict:
		response = self._request("POST", "/price_rules.json", payload={"price_rule": payload})
		return response.json()["price_rule"]

	def create_discount_code(self, price_rule_id: int, code_payload: Dict) -> Dict:
		response = self._request(
			"POST",
			f"/price_rules/{price_rule_id}/discount_codes.json",
			payload={"discount_code": code_payload},
		)
		return response.json()["discount_code"]

	def iterate_metafield_definitions(self, owner_type: Optional[str] = None) -> Iterable[Dict]:
		query = """
		query ListMetafieldDefinitions($first: Int!, $cursor: String, $ownerType: MetafieldOwnerType) {
				edges {
					cursor
					node {
						id
						name
						namespace
						key
						description
						type
						validationRules
						ownerType
						visibleToStorefrontApi
						standardMetafield
						pin
					}
				}
				pageInfo { hasNextPage endCursor }
			}
		}
		"""
		variables = {"first": 100, "cursor": None, "ownerType": owner_type.upper() if owner_type else None}
		while True:
			data = self.graphql(query, variables)
			edges = _safe_get(data, "metafieldDefinitions", "edges", default=[])
			for edge in edges:
				yield edge["node"]
			page_info = _safe_get(data, "metafieldDefinitions", "pageInfo", default={})
			if not page_info or not page_info.get("hasNextPage"):
				break
			variables["cursor"] = page_info.get("endCursor")

	def find_metafield_definition(self, owner_type: str, namespace: str, key: str) -> Optional[Dict]:
		params = {
			"owner_type": owner_type,
			"namespace": namespace,
			"key": key,
		}
		try:
			response = self._request("GET", "/metafield_definitions.json", params=params)
		except ShopifyAPIError as exc:
			if "404" in str(exc):
				return None
			raise
		definitions = response.json().get("metafield_definitions", [])
		return definitions[0] if definitions else None

	def create_metafield_definition(self, definition_payload: Dict) -> Dict:
		allowed = {
			"name",
			"namespace",
			"key",
			"description",
			"owner_type",
			"type",
			"validation_rules",
			"visible_to_storefront_api",
			"pin",
			"standard_metafield",
		}
		rest_payload = {}
		for camel_case, snake_case in [
			("name", "name"),
			("namespace", "namespace"),
			("key", "key"),
			("description", "description"),
			("ownerType", "owner_type"),
			("type", "type"),
			("validationRules", "validation_rules"),
			("visibleToStorefrontApi", "visible_to_storefront_api"),
			("pin", "pin"),
			("standardMetafield", "standard_metafield"),
		]:
			value = definition_payload.get(camel_case)
			if value is None or snake_case not in allowed:
				continue
			if camel_case == "ownerType" and isinstance(value, str):
				rest_payload[snake_case] = value.lower()
			else:
				rest_payload[snake_case] = value

		response = self._request(
			"POST",
			"/metafield_definitions.json",
			payload={"metafield_definition": rest_payload},
		)
		return response.json().get("metafield_definition")


def _sanitize_variants(variants: Sequence[Dict]) -> List[Dict]:
	sanitized: List[Dict] = []
	for variant in variants:
		payload = {
			"title": variant.get("title"),
			"sku": variant.get("sku"),
			"price": variant.get("price"),
			"compare_at_price": variant.get("compare_at_price"),
			"option1": variant.get("option1"),
			"option2": variant.get("option2"),
			"option3": variant.get("option3"),
			"taxable": variant.get("taxable", True),
			"inventory_management": variant.get("inventory_management"),
			"inventory_policy": variant.get("inventory_policy", "deny"),
			"requires_shipping": variant.get("requires_shipping", True),
			"grams": variant.get("grams", 0),
			"weight": variant.get("weight", 0),
			"weight_unit": variant.get("weight_unit", "g"),
			"barcode": variant.get("barcode"),
			"inventory_quantity": variant.get("inventory_quantity", 0),
		}
		# Only allow fulfillment_service if it's explicitly "manual"; drop invalid values like "gift_card"
		fs = variant.get("fulfillment_service")
		if fs == "manual" or fs is None:
			payload["fulfillment_service"] = "manual"
		# else: skip adding, let Shopify default or app assignment handle it
		sanitized.append({k: v for k, v in payload.items() if v not in (None, "")})
	return sanitized


def _sanitize_options(options: Sequence[Dict]) -> List[Dict]:
	cleaned = []
	for option in options:
		cleaned.append(
			{
				"name": option.get("name"),
				"position": option.get("position"),
				"values": option.get("values", []),
			}
		)
	return cleaned


def _sanitize_images(images: Sequence[Dict]) -> List[Dict]:
	sanitized = []
	for image in images:
		sanitized.append(
			{
				"attachment": image.get("attachment"),
				"src": image.get("src"),
				"position": image.get("position"),
				"alt": image.get("alt"),
			}
		)
	return sanitized


def _sanitize_product(product: Dict) -> Dict:
	title = product.get("title", "Untitled Product")
	payload = {
		"title": title,
		"body_html": product.get("body_html"),
		"vendor": product.get("vendor"),
		"product_type": product.get("product_type"),
		"tags": product.get("tags"),
		"template_suffix": product.get("template_suffix"),
		"status": product.get("status", "active"),
		"handle": product.get("handle") or _slugify(title),
		"options": _sanitize_options(product.get("options", [])),
		"variants": _sanitize_variants(product.get("variants", [])),
		"images": _sanitize_images(product.get("images", [])),
	}
	metafields_global_title = product.get("metafields_global_title_tag")
	metafields_global_description = product.get("metafields_global_description_tag")
	if metafields_global_title:
		payload["metafields_global_title_tag"] = metafields_global_title
	if metafields_global_description:
		payload["metafields_global_description_tag"] = metafields_global_description
	return payload


def _encode_asset(asset: Dict) -> Dict:
	if "value" in asset:
		return {"key": asset["key"], "value": asset["value"]}
	if "attachment" in asset:
		return {"key": asset["key"], "attachment": asset["attachment"]}
	if "public_url" in asset:
		response = requests.get(asset["public_url"], timeout=DEFAULT_TIMEOUT)
		response.raise_for_status()
		encoded = base64.b64encode(response.content).decode("utf-8")
		return {"key": asset["key"], "attachment": encoded}
	return {"key": asset["key"], "value": ""}


def _asset_priority(key: str) -> int:
	if key.startswith("sections/"):
		return 0
	if key.startswith("snippets/"):
		return 1
	if key.startswith("layout/"):
		return 2
	if key.startswith("templates/"):
		return 3
	if key.startswith("config/"):
		return 4
	if key.startswith("locales/"):
		return 5
	return 6


def _sanitize_metafield_definition(definition: Dict) -> Dict:
	field_map = {
		"name": "name",
		"namespace": "namespace",
		"key": "key",
		"description": "description",
		"ownerType": "ownerType",
		"type": "type",
		"validationRules": "validationRules",
		"visibleToStorefrontApi": "visibleToStorefrontApi",
		"pin": "pin",
		"standardMetafield": "standardMetafield",
	}
	payload = {}
	for source_field, target_field in field_map.items():
		value = definition.get(source_field)
		if value is not None and value != []:
			payload[target_field] = value
	return payload


def _extract_metafield_payload(metafield: Dict) -> Dict:
	keys = [
		"namespace",
		"key",
		"type",
		"value",
		"description",
	]
	payload = {key: metafield.get(key) for key in keys if metafield.get(key) is not None}
	payload["owner_resource"] = "shop"
	return payload


@dataclass
class CloneSummary:
	products_created: int = 0
	products_skipped: int = 0
	themes_created: int = 0
	metafield_definitions_created: int = 0
	metafields_created: int = 0
	apps_documented: int = 0
	issues: List[str] = field(default_factory=list)


def _is_reference_metafield_type(type_str: Optional[str]) -> bool:
	if not type_str:
		return False
	t = type_str.lower()
	return (
		"reference" in t
		or "media_image" in t
		or t in {
			"file_reference",
			"product_reference",
			"collection_reference",
			"variant_reference",
			"page_reference",
		}
	)


def _should_skip_metafield_due_to_reference(field: Dict) -> Tuple[bool, str]:
	# Skip metafields that reference other resources which won't exist with the same GIDs on the target store
	mf_type = field.get("type")
	if _is_reference_metafield_type(mf_type):
		return True, f"metafield type '{mf_type}' references external resources"
	val = field.get("value")
	if isinstance(val, str) and val.startswith("gid://"):
		return True, "metafield value references a resource GID not present on target"
	return False, ""


class StoreCloneJob:
	"""Coordinate cloning different resources from source to target."""

	def __init__(
		self,
		source: ShopifyAdminAPI,
		target: ShopifyAdminAPI,
		*,
		resources: Sequence[str],
		overwrite: bool,
		dry_run: bool,
		report_dir: str,
		theme_name: Optional[str] = None,
		progress: Optional[ProgressManager] = None,
	) -> None:
		self.source = source
		self.target = target
		self.resources = {resource.lower() for resource in resources}
		self.overwrite = overwrite
		self.dry_run = dry_run
		self.report_dir = report_dir
		self.theme_name = theme_name
		self.summary = CloneSummary()
		self.progress = progress or ProgressManager()

	def run(self) -> CloneSummary:
		if "products" in self.resources:
			self._clone_products()
		if "metafields" in self.resources:
			self._clone_metafield_definitions()
		if "themes" in self.resources or "theme" in self.resources:
			self._clone_theme()
		if "settings" in self.resources:
			self._clone_settings()
		if "apps" in self.resources:
			self._document_apps()
		return self.summary

	# --------------------------------------------------------------
	# Individual clone steps
	# --------------------------------------------------------------

	def _estimate_product_total(self) -> Optional[int]:
		try:
			return self.source.count_products()
		except ShopifyAPIError as exc:
			self.progress.announce(f"Unable to determine product count: {exc}")
			return None

	def _clone_products(self) -> None:
		self.progress.announce("Cloning products")
		total = self._estimate_product_total()
		with self.progress.task("products", total=total, label="Products") as progress_bar:
			for product in self.source.iterate("/products.json", "products"):
				payload = _sanitize_product(product)
				existing_id = self.target.product_exists(payload["handle"])

				if existing_id and not self.overwrite:
					self.summary.products_skipped += 1
					progress_bar.update(1)
					continue

				if self.dry_run:
					self.summary.products_created += 1
					progress_bar.update(1)
					continue

				if existing_id and self.overwrite:
					self.target.delete_product(existing_id)

				created = self.target.create_product(payload)
				self.summary.products_created += 1

				metafields = list(
					self.source.iterate(
						f"/products/{product['id']}/metafields.json",
						"metafields",
					)
				)
				if metafields:
					for metafield in metafields:
						field_payload = {
							key: metafield.get(key)
							for key in ["namespace", "key", "value", "type", "description"]
							if metafield.get(key) is not None
						}
						field_payload["owner_resource"] = "product"
						field_payload["owner_id"] = created["id"]

						# Skip metafields that reference resources which cannot be remapped safely
						should_skip, reason = _should_skip_metafield_due_to_reference(field_payload)
						if should_skip:
							self.summary.issues.append(
								f"Skipped product metafield {field_payload.get('namespace')}::{field_payload.get('key')} on {payload.get('handle')} - {reason}"
							)
							continue

						if not self.dry_run:
							try:
								self.target._request(
									"POST",
									"/metafields.json",
									payload={"metafield": field_payload},
								)
							except ShopifyAPIError as exc:
								self.summary.issues.append(
									f"Failed to create product metafield {field_payload.get('namespace')}::{field_payload.get('key')} on {payload.get('handle')}: {exc}"
								)

				progress_bar.update(1)

	def _clone_theme(self) -> None:
		themes = self.source.list_themes()
		main_theme = next((theme for theme in themes if theme.get("role") == "main"), None)
		if not main_theme:
			raise ShopifyAPIError("Source store does not expose a main theme to clone")

		self.progress.announce("Cloning theme assets")
		assets = self.source.list_theme_assets(main_theme["id"])
		assets = sorted(
			assets,
			key=lambda asset: (_asset_priority(asset.get("key", "")), asset.get("key", "")),
		)
		target_name = self.theme_name or f"{main_theme['name']} (Cloned)"

		if self.dry_run:
			self.summary.themes_created += 1
			with self.progress.task("theme", total=len(assets) or None, label="Theme assets") as progress_bar:
				for _ in assets:
					progress_bar.update(1)
			return

		target_themes = self.target.list_themes()
		existing = next((theme for theme in target_themes if theme.get("name") == target_name), None)

		if existing and self.overwrite:
			self.target.delete_theme(existing["id"])
			existing = None

		if existing:
			target_theme_id = existing["id"]
		else:
			created_theme = self.target.create_theme(target_name)
			target_theme_id = created_theme["id"]
			self.summary.themes_created += 1

		theme_errors: List[str] = []
		with self.progress.task("theme", total=len(assets) or None, label="Theme assets") as progress_bar:
			for asset in assets:
				key = asset.get("key", "")
				try:
					detailed = self.source.get_theme_asset(main_theme["id"], key)
					encoded = _encode_asset(detailed)
					self.target.upsert_theme_asset(target_theme_id, encoded)
				except ShopifyAPIError as exc:
					message = f"Failed to sync asset {key}: {exc}"
					self.progress.announce(message)
					theme_errors.append(message)
				finally:
					progress_bar.update(1)

		if theme_errors:
			self.summary.issues.extend(theme_errors)

	def _clone_metafield_definitions(self) -> None:
		self.progress.announce("Cloning metafield definitions")
		owner_whitelist = {
			"product",
			"variant",
			"product_variant",
			"product_option",
			"product_image",
			"collection",
			"shop",
		}
		definitions = []
		seen_definitions = set()
		for owner in owner_whitelist:
			graphql_owner = owner.upper()
			try:
				for definition in self.source.iterate_metafield_definitions(graphql_owner):
					if definition.get("standardMetafield"):
						continue
					fingerprint = (
						definition.get("ownerType"),
						definition.get("namespace"),
						definition.get("key"),
					)
					if fingerprint in seen_definitions:
						continue
					seen_definitions.add(fingerprint)
					definitions.append(definition)
			except ShopifyAPIError as exc:
				message = f"Unable to list metafield definitions for owner {graphql_owner}: {exc}"
				self.progress.announce(message)
				self.summary.issues.append(message)
				continue
		if not definitions:
			return

		with self.progress.task(
			"metafields",
			total=len(definitions),
			label="Metafield definitions",
		) as progress_bar:
			for definition in definitions:
				try:
					owner_type = definition.get("ownerType")
					namespace = definition.get("namespace")
					key = definition.get("key")
					if not owner_type or not namespace or not key:
						continue

					existing = self.target.find_metafield_definition(owner_type.lower(), namespace, key)
					if existing:
						continue

					if self.dry_run:
						self.summary.metafield_definitions_created += 1
						continue

					payload = _sanitize_metafield_definition(definition)
					self.target.create_metafield_definition(payload)
					self.summary.metafield_definitions_created += 1
				except ShopifyAPIError as exc:
					message = (
						f"Failed to create metafield definition {definition.get('namespace')}::{definition.get('key')}: {exc}"
					)
					self.progress.announce(message)
					self.summary.issues.append(message)
				finally:
					progress_bar.update(1)

	def _clone_settings(self) -> None:
		self.progress.announce("Cloning shop metafields")
		metafields = list(self.source.iterate_shop_metafields())
		with self.progress.task("settings", total=len(metafields) or None, label="Shop metafields") as progress_bar:
			if self.dry_run:
				self.summary.metafields_created += len(metafields)
				for _ in metafields:
					progress_bar.update(1)
				return

			target_shop_id = self.target.get_shop()["id"]
			for metafield in metafields:
				payload = _extract_metafield_payload(metafield)
				payload["owner_id"] = target_shop_id
				# Skip reference-type shop metafields as they likely point to non-existent GIDs
				should_skip, reason = _should_skip_metafield_due_to_reference(payload)
				if should_skip:
					self.summary.issues.append(
						f"Skipped shop metafield {payload.get('namespace')}::{payload.get('key')} - {reason}"
					)
					progress_bar.update(1)
					continue
				try:
					self.target.create_metafield(payload)
					self.summary.metafields_created += 1
				except ShopifyAPIError as exc:
					self.summary.issues.append(
						f"Failed to create shop metafield {payload.get('namespace')}::{payload.get('key')}: {exc}"
					)
				finally:
					progress_bar.update(1)

	def _document_apps(self) -> None:
		self.progress.announce("Documenting installed apps")
		query = """
		query ListApps($cursor: String) {
			appInstallations(first: 100, after: $cursor) {
				edges {
					cursor
					node {
						id
						app { title handle developerName }
						launchUrl
						installedAt
					}
				}
				pageInfo { hasNextPage endCursor }
			}
		}
		"""

		installations: List[Dict] = []
		cursor: Optional[str] = None
		while True:
			data = self.source.graphql(query, {"cursor": cursor})
			edges = _safe_get(data, "appInstallations", "edges", default=[])
			for edge in edges:
				installations.append(edge["node"])
			page_info = _safe_get(data, "appInstallations", "pageInfo", default={})
			if not page_info or not page_info.get("hasNextPage"):
				break
			cursor = page_info.get("endCursor")

		with self.progress.task("apps", total=len(installations) or None, label="Apps") as progress_bar:
			for _ in installations:
				progress_bar.update(1)

		self.summary.apps_documented = len(installations)
		if self.dry_run or not installations:
			return

		os.makedirs(self.report_dir, exist_ok=True)
		report_path = os.path.join(
			self.report_dir, f"{_slugify(self.target.store_domain)}-apps.json"
		)
		with open(report_path, "w", encoding="utf-8") as handle:
			json.dump(installations, handle, indent=2)


class TestDataSeeder:
	"""Provision rich test data into a development store."""

	def __init__(
		self,
		api: ShopifyAdminAPI,
		*,
		prefix: str,
		include: Sequence[str],
		dry_run: bool,
	) -> None:
		self.api = api
		self.prefix = prefix.strip()
		self.include = {item.lower() for item in include}
		self.dry_run = dry_run
		self.created: Dict[str, List[Dict]] = {
			"products": [],
			"customers": [],
			"orders": [],
			"discounts": [],
		}

	def run(self) -> Dict[str, List[Dict]]:
		products_map: Dict[str, Dict] = {}
		if "products" in self.include:
			products_map = self._seed_products()
		if "customers" in self.include:
			self._seed_customers()
		if "orders" in self.include and products_map:
			self._seed_orders(products_map)
		if "discounts" in self.include:
			self._seed_discounts()
		return self.created

	# --------------------------------------------------------------
	# Seed helpers
	# --------------------------------------------------------------

	def _seed_products(self) -> Dict[str, Dict]:
		catalog = {
			"backpack": {
				"title": f"{self.prefix} Alpine Backpack",
				"product_type": "Backpacks",
				"vendor": "TES Lab",
				"tags": "outdoor,alpinesports,tes-seed",
				"body_html": "<p>Versatile backpack ready for alpine adventures.</p>",
				"variants": [
					{"option1": "45L", "price": "189.00", "sku": "TES-ALP-45"},
					{"option1": "60L", "price": "219.00", "sku": "TES-ALP-60"},
				],
				"options": [{"name": "Capacity", "values": ["45L", "60L"]}],
				"images": [
					{
						"src": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
						"alt": "Backpack on a mountain ridge",
					}
				],
			},
			"espresso": {
				"title": f"{self.prefix} Espresso Beans",
				"product_type": "Grocery",
				"vendor": "TES Lab",
				"tags": "coffee,tes-seed,subscription",
				"body_html": "<p>Single origin espresso roast ideal for subscription plans.</p>",
				"variants": [
					{"option1": "Whole Beans", "price": "16.50", "sku": "TES-ESP-WB"},
					{"option1": "Ground", "price": "17.50", "sku": "TES-ESP-GR"},
				],
				"options": [{"name": "Grind", "values": ["Whole Beans", "Ground"]}],
				"images": [
					{
						"src": "https://images.unsplash.com/photo-1447933601403-0c6688de566e",
						"alt": "Coffee beans spilling from a bag",
					}
				],
			},
			"addon": {
				"title": f"{self.prefix} Digital Trail Map",
				"product_type": "Digital",
				"vendor": "TES Lab",
				"tags": "digital,download,tes-seed",
				"body_html": "<p>Digital GPX trail map download with lifetime updates.</p>",
				"variants": [
					{"option1": "Standard", "price": "9.99", "sku": "TES-MAP-STD", "requires_shipping": False},
				],
				"options": [{"name": "License", "values": ["Standard"]}],
				"images": [
					{
						"src": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
						"alt": "Trail map on a tablet",
					}
				],
			},
		}

		created_map: Dict[str, Dict] = {}

		for key, product in catalog.items():
			payload = {
				"title": product["title"],
				"body_html": product["body_html"],
				"vendor": product["vendor"],
				"product_type": product["product_type"],
				"tags": product["tags"],
				"options": product["options"],
				"variants": product["variants"],
				"images": product.get("images", []),
				"handle": _slugify(product["title"]),
				"status": "active",
			}

			existing_id = self.api.product_exists(payload["handle"])
			if existing_id:
				continue

			if self.dry_run:
				fake_product = payload.copy()
				fake_product["id"] = 0
				fake_product["variants"] = []
				created_map[key] = fake_product
				self.created["products"].append(fake_product)
				continue

			created = self.api.create_product(payload)
			created_map[key] = created
			self.created["products"].append(created)

		return created_map

	def _seed_customers(self) -> None:
		customers = [
			{
				"first_name": "Anna",
				"last_name": "Schneider",
				"email": f"anna.schneider+tes@tes.example",
				"addresses": [
					{
						"address1": "Bergstrasse 12",
						"city": "Munich",
						"country_code": "DE",
						"zip": "80331",
					}
				],
				"tags": "tes-seed,de,europe",
				"locale": "de-DE",
			},
			{
				"first_name": "Luc",
				"last_name": "Dubois",
				"email": f"luc.dubois+tes@tes.example",
				"addresses": [
					{
						"address1": "8 Rue de Lyon",
						"city": "Paris",
						"country_code": "FR",
						"zip": "75012",
					}
				],
				"tags": "tes-seed,fr,europe",
				"locale": "fr-FR",
			},
			{
				"first_name": "Mara",
				"last_name": "Gerber",
				"email": f"mara.gerber+tes@tes.example",
				"addresses": [
					{
						"address1": "Seefeldstrasse 88",
						"city": "Zurich",
						"country_code": "CH",
						"zip": "8008",
					}
				],
				"tags": "tes-seed,ch,europe",
				"locale": "de-CH",
			},
			{
				"first_name": "Jordan",
				"last_name": "Coleman",
				"email": f"jordan.coleman+tes@tes.example",
				"addresses": [
					{
						"address1": "1420 Castro St",
						"city": "Mountain View",
						"country_code": "US",
						"province_code": "CA",
						"zip": "94041",
					}
				],
				"tags": "tes-seed,us,north-america",
				"locale": "en-US",
			},
		]

		for customer in customers:
			existing = self.api.search_customers(f"email:{customer['email']}")
			if existing:
				continue
			if self.dry_run:
				self.created["customers"].append(customer)
				continue
			created = self.api.create_customer(customer)
			self.created["customers"].append(created)

	def _seed_orders(self, products_map: Dict[str, Dict]) -> None:
		if not products_map:
			return

		def _variant(product_key: str, index: int = 0) -> Optional[int]:
			product = products_map.get(product_key)
			if not product:
				return None
			variants = product.get("variants", [])
			if index >= len(variants):
				return None
			return variants[index]["id"] if variants[index].get("id") else None

		scenarios = [
			{
				"email": "anna.schneider+tes@tes.example",
				"shipping_address": {
					"address1": "Bergstrasse 12",
					"city": "Munich",
					"country_code": "DE",
					"zip": "80331",
				},
				"billing_address": {
					"address1": "Bergstrasse 12",
					"city": "Munich",
					"country_code": "DE",
					"zip": "80331",
				},
				"line_items": [
					{"variant_id": _variant("backpack"), "quantity": 1},
					{"variant_id": _variant("addon"), "quantity": 1},
				],
				"shipping_lines": [
					{"title": "DHL Paket", "price": "8.90", "code": "DHL"}
				],
				"currency": "EUR",
			},
			{
				"email": "luc.dubois+tes@tes.example",
				"shipping_address": {
					"address1": "8 Rue de Lyon",
					"city": "Paris",
					"country_code": "FR",
					"zip": "75012",
				},
				"billing_address": None,
				"line_items": [
					{"variant_id": _variant("espresso", 0), "quantity": 2},
				],
				"shipping_lines": [
					{"title": "Colissimo", "price": "6.50", "code": "COLISSIMO"}
				],
				"currency": "EUR",
			},
			{
				"email": "mara.gerber+tes@tes.example",
				"shipping_address": {
					"address1": "Seefeldstrasse 88",
					"city": "Zurich",
					"country_code": "CH",
					"zip": "8008",
				},
				"billing_address": None,
				"line_items": [
					{"variant_id": _variant("backpack", 1), "quantity": 1},
				],
				"shipping_lines": [
					{"title": "Swiss Post Priority", "price": "12.00", "code": "SWISSPOST"}
				],
				"currency": "CHF",
			},
			{
				"email": "jordan.coleman+tes@tes.example",
				"shipping_address": {
					"address1": "1420 Castro St",
					"city": "Mountain View",
					"country_code": "US",
					"province_code": "CA",
					"zip": "94041",
				},
				"billing_address": {
					"address1": "1420 Castro St",
					"city": "Mountain View",
					"country_code": "US",
					"province_code": "CA",
					"zip": "94041",
				},
				"line_items": [
					{"variant_id": _variant("espresso", 1), "quantity": 1},
					{"variant_id": _variant("addon"), "quantity": 1},
				],
				"shipping_lines": [
					{"title": "UPS Ground", "price": "14.00", "code": "UPS"}
				],
				"currency": "USD",
			},
		]

		for scenario in scenarios:
			line_items = []
			for index, item in enumerate(scenario["line_items"]):
				variant_id = item.get("variant_id")
				if variant_id is None and self.dry_run:
					variant_id = index + 1
				line_items.append({"variant_id": variant_id, "quantity": item["quantity"]})

			if any(item["variant_id"] is None for item in line_items):
				continue

			payload = {
				"email": scenario["email"],
				"line_items": line_items,
				"shipping_address": scenario["shipping_address"],
				"billing_address": scenario["billing_address"],
				"shipping_lines": scenario["shipping_lines"],
				"financial_status": "paid",
				"fulfillment_status": "fulfilled",
				"currency": scenario["currency"],
				"tags": "tes-seed",
				"test": True,
			}
			if self.dry_run:
				self.created["orders"].append(payload)
				continue
			created = self.api.create_order(payload)
			self.created["orders"].append(created)

	def _seed_discounts(self) -> None:
		price_rules = [
			{
				"title": f"{self.prefix} Alpine Launch",
				"target_type": "line_item",
				"target_selection": "entitled",
				"allocation_method": "percentage",
				"entitled_collection_ids": [],
				"entitled_product_ids": [],
				"value_type": "percentage",
				"value": "-15.0",
				"customer_selection": "all",
				"usage_limit": 100,
				"starts_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
			},
			{
				"title": f"{self.prefix} Free EU Shipping",
				"target_type": "shipping_line",
				"target_selection": "all",
				"allocation_method": "across",
				"value_type": "percentage",
				"value": "-100.0",
				"customer_selection": "all",
				"usage_limit": 200,
				"starts_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
			},
		]

		codes = [
			{"code": "TES-ALPINE-15"},
			{"code": "TES-FREE-EU"},
		]

		for price_rule, code in zip(price_rules, codes):
			if self.dry_run:
				self.created["discounts"].append({"price_rule": price_rule, "code": code})
				continue
			created_rule = self.api.create_price_rule(price_rule)
			created_code = self.api.create_discount_code(created_rule["id"], code)
			self.created["discounts"].append(
				{"price_rule": created_rule, "discount_code": created_code}
			)


DEFAULT_CLONE_RESOURCES = ("products", "themes", "metafields", "settings", "apps")
DEFAULT_SEED_COMPONENTS = ("products", "customers", "orders", "discounts")


def _ensure_store_value(value: Optional[str], prompt_text: str) -> str:
	if value and value.strip():
		return value.strip()
	response = click.prompt(prompt_text, type=str).strip()
	if not response:
		raise click.BadParameter(f"{prompt_text} cannot be empty")
	return response


def _parse_resource_list(raw_value: str) -> List[str]:
	items = [segment.strip().lower() for segment in raw_value.split(",") if segment.strip()]
	valid = {item.lower() for item in DEFAULT_CLONE_RESOURCES}
	if not items:
		return list(DEFAULT_CLONE_RESOURCES)
	if not set(items).issubset(valid):
		raise click.BadParameter(
			"Invalid resource selection. Choose any of: " + ", ".join(DEFAULT_CLONE_RESOURCES)
		)
	return items


def _resolve_resources(resources: Sequence[str]) -> List[str]:
	if resources:
		return [item.lower() for item in resources]
	default_selection = ",".join(DEFAULT_CLONE_RESOURCES)
	selection = click.prompt(
		"Select resources to sync (comma separated)",
		default=default_selection,
	)
	return _parse_resource_list(selection)


def _maybe_store_target_token(store_domain: str, token: str) -> None:
	if not token:
		return
	if not click.confirm("Save the target token to .tes.yml for future runs?", default=False):
		return
	config = utils.get_config()
	shopify_cfg = config.setdefault("shopify", {})
	stores_cfg = shopify_cfg.setdefault("stores", {})
	store_entry = stores_cfg.setdefault(store_domain, {})
	if store_entry.get("access_token") == token:
		click.echo(f"Token for {store_domain} already stored; nothing to update.")
		return
	store_entry["access_token"] = token
	utils.write_config(config)
	click.echo(f"Stored token for {store_domain} in .tes.yml")


@click.group()
@click.pass_context
def store(ctx):
	"""Shopify storefront level utilities."""


@store.command()
@click.option("--source-store", required=False, help="Source store domain (with or without .myshopify.com)")
@click.option(
	"--source-token",
	envvar="TES_SHOPIFY_SOURCE_TOKEN",
	prompt=True,
	hide_input=True,
	help="Admin API access token for the source store",
)
@click.option("--target-store", required=False, help="Target development store domain")
@click.option(
	"--target-token",
	envvar="TES_SHOPIFY_TARGET_TOKEN",
	prompt=True,
	hide_input=True,
	help="Admin API access token for the target store",
)
@click.option(
	"--resource",
	"resources",
	multiple=True,
	type=click.Choice(["products", "themes", "metafields", "settings", "apps"], case_sensitive=False),
	help="Limit cloning to specific resources. Defaults to all.",
)
@click.option("--overwrite/--no-overwrite", default=False, help="Overwrite resources that already exist on the target store")
@click.option("--dry-run/--apply", default=False, help="Show what would be cloned without making changes")
@click.option("--theme-name", help="Optional name for the cloned theme on the target store")
@click.option(
	"--report-dir",
	default="shopify_clone_reports",
	show_default=True,
	help="Directory for generated reports such as installed app lists",
)
def clone(
	source_store: str,
	source_token: str,
	target_store: str,
	target_token: str,
	resources: Sequence[str],
	overwrite: bool,
	dry_run: bool,
	theme_name: Optional[str],
	report_dir: str,
):
	"""Clone data from a source store into a development store."""

	source_store = _ensure_store_value(source_store, "Source store")
	target_store = _ensure_store_value(target_store, "Target store")
	selected_resources = _resolve_resources(resources)
	if "themes" in selected_resources and "metafields" not in selected_resources:
		selected_resources.append("metafields")
		click.echo("Metafields required for theme sync; adding 'metafields' to resource list.")
	selected_resources = list(dict.fromkeys(selected_resources))
	click.echo(
		f"Cloning resources {', '.join(selected_resources)} from {source_store} to {target_store}"
	)
	if dry_run:
		click.echo("Running in dry-run mode; no changes will be applied.")

	_maybe_store_target_token(target_store, target_token)

	source = ShopifyAdminAPI(source_store, source_token)
	target = ShopifyAdminAPI(target_store, target_token)
	progress = ClickProgressManager()
	job = StoreCloneJob(
		source,
		target,
		resources=selected_resources,
		overwrite=overwrite,
		dry_run=dry_run,
		report_dir=report_dir,
		theme_name=theme_name,
		progress=progress,
	)
	summary = job.run()

	click.echo("Clone complete:")
	click.echo(f"  Products created: {summary.products_created}")
	click.echo(f"  Products skipped: {summary.products_skipped}")
	click.echo(f"  Themes created: {summary.themes_created}")
	click.echo(f"  Metafield definitions created: {summary.metafield_definitions_created}")
	click.echo(f"  Shop metafields copied: {summary.metafields_created}")
	click.echo(f"  Apps documented: {summary.apps_documented}")
	if summary.issues:
		click.echo("Issues encountered:")
		for issue in summary.issues:
			click.echo(f"  - {issue}")


@store.command()
@click.option("--store", "store_domain", required=True, help="Store domain to seed test data into")
@click.option(
	"--token",
	envvar="TES_SHOPIFY_ACCESS_TOKEN",
	prompt=True,
	hide_input=True,
	help="Admin API access token with write rights",
)
@click.option(
	"--include",
	multiple=True,
	type=click.Choice(["products", "customers", "orders", "discounts"], case_sensitive=False),
	help="Choose which resource types to seed. Defaults to all.",
)
@click.option("--prefix", default="TES Seed", show_default=True, help="Prefix for generated resources")
@click.option("--dry-run/--apply", default=False, help="Preview the payloads without creating data")
def seed(
	store_domain: str,
	token: str,
	include: Sequence[str],
	prefix: str,
	dry_run: bool,
):
	"""Fill a development store with diversified test data."""

	include_set = include or DEFAULT_SEED_COMPONENTS
	click.echo(f"Seeding {', '.join(include_set)} into {store_domain}")
	if dry_run:
		click.echo("Running in dry-run mode; payloads will not be created.")

	api = ShopifyAdminAPI(store_domain, token)
	seeder = TestDataSeeder(api, prefix=prefix, include=include_set, dry_run=dry_run)
	results = seeder.run()

	click.echo("Seed results:")
	for key in DEFAULT_SEED_COMPONENTS:
		if key in results:
			click.echo(f"  {key.capitalize()}: {len(results[key])}")
