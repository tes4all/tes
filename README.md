# tes

TES - Tools for Shopify theme management and Git operations

## Installation

Install the CLI tool using pipx (recommended):

```bash
pipx install git+https://github.com/tes4all/tes.git
```

Or using pip:

```bash
pip install git+https://github.com/tes4all/tes.git
```

## Usage

After installation, you can use the `tes` command:

```bash
tes --help
```

### Shopify Commands

Manage Shopify themes:

```bash
tes shopify theme init --store your-store-name
tes shopify theme update
tes shopify printess update
```

### Git Commands

Manage Git repositories:

```bash
tes git tools status --dir /path/to/repos
tes git tools update --dir /path/to/repos
```

## Why OpenTofu?

It would be easier for me to write IaC code in the language I'm most comfortable with. But here is the problem: some of you don't like or know the language I am using. So it's hard to find the best language for all of you. So I decided to use OpenTofu as the default language for IaC code.

