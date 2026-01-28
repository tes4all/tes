Here is a comprehensive plan you can paste directly to your VS Code Agent. It instructs the agent to restructure your repository from a "single project" format into a "Golden Stack Library" that other repos can consume.

### The Goal
Restructure the `tes` repo so it serves as a library of reusable Stack definitions. This involves separating **Dockerfiles** (the build process) from **Compose Files** (the deployment definition) and organizing them by capability.

---

### Phase 1: Directory Restructuring
**Prompt for Agent:**
```text
I need to restructure this repository to act as a shared library for Docker Swarm stacks.
Please perform the following file operations:

1. Create a root directory called `stacks`.
2. Inside `stacks`, create a subdirectory called `edge-router`.
3. Create a root directory called `images`.
4. Inside `images`, create subdirectories `haproxy` and `traefik`.
5. Move `Dockerfile.haproxy` to `images/haproxy/Dockerfile` and any related config files there.
6. Move `Dockerfile.traefik` to `images/traefik/Dockerfile`.
7. Move the main YAML content relevant to the router into `stacks/edge-router/compose.yaml`.
```

### Phase 2: Sanitizing the Golden Stack (The YAML Edit)
**Prompt for Agent:**
```text
Now, edit `stacks/edge-router/compose.yaml` to make it ready for remote consumption via `include`.
Apply these specific changes:

1. REMOVE the `build:` blocks completely. (We assume images are built by CI separately).
2. Parameterize the `image:` keys. Change them to:
   - `image: ${REGISTRY:-ghcr.io/tes4all}/haproxy:${HAPROXY_VERSION:-2.9.12}`
   - `image: ${REGISTRY:-ghcr.io/tes4all}/traefik:${TRAEFIK_VERSION:-3.2.3}`
   (Replace `ghcr.io/tes4all` with your actual registry namespace if different).
3. Ensure all numbers in the `cpus` fields allow string format (e.g., keep them quoted as "0.5").
4. Keep the `deploy:`, `networks:`, and `volumes:` sections exactly as they are.
```

### Phase 3: Create a Local Development Override (Optional but recommended)
**Prompt for Agent:**
```text
Create a new file in the root called `compose.dev.yaml` for local testing/building.
This file should use the `include` feature to pull in the golden stack and add build contexts back in.

Content suggestion:
```yaml
include:
  - path: ./stacks/edge-router/compose.yaml

services:
  haproxy:
    build:
      context: ./images/haproxy
  traefik:
    build:
      context: ./images/traefik
```
```

### Phase 4: Create the "Consumer" Example
**Prompt for Agent:**
```text
Create a `README.md` file in `stacks/edge-router/` explaining how other repos should use this stack.
Include this code block as an example:

## How to use in your project
In your project's `compose.yaml`:

```yaml
include:
  - git: https://github.com/tes4all/tes.git
    ref: main
    file: stacks/edge-router/compose.yaml

services:
  # You can override environment variables here
  traefik:
    environment:
      - ACME_EMAIL=admin@my-new-project.com
```
```

---

### What this accomplishes

1.  **Cleaner File Structure:**
    *   `stacks/edge-router/compose.yaml` is now pure configuration. It contains no messy build logic, only deployment logic.
2.  **Versioning Support:**
    *   By using `${HAPROXY_VERSION:-2.9.12}`, your consumer repos can override the version if they need a specific update, or fall back to the default you defined in the golden stack.
3.  **CI/CD Friendly:**
    *   Your CI system can specifically watch the `images/` folder to trigger builds, and the `stacks/` folder to trigger deployments.
4.  **Swarm Compliance:**
    *   By removing the `build` block from the main YAML, you eliminate warnings when running `docker stack deploy`.
