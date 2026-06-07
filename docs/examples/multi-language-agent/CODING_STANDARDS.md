# Coding Standards

## Go services (`services/*/`)

- Use `gofmt`-compliant formatting. Never submit unformatted code.
- Package names are lowercase, single words, no underscores: `auth`, `store`, `ingest`.
- Exported names are PascalCase; unexported names are camelCase.
- Acronyms follow Go convention: `ID`, `URL`, `HTTP`, `API` (not `Id`, `Url`, `Http`).
- Wrap errors with `fmt.Errorf("context: %w", err)` to preserve the chain. Never swallow them silently.
- Define interfaces in the **consumer** package, not the implementor package. Prefer one-method interfaces.
- Use hand-written fakes (`Fake<InterfaceName>`) that implement the relevant interface — no `mockery` or mock-generation tools.
- Each service has its own `go.mod` inside the Go workspace (`go.work` at repo root). Shared types live in `internal/`.

## TypeScript frontend (`web/`)

- Format with `prettier`; lint with the repo's `eslint` config — both run via `npm run check`.
- Components are function components with hooks; no class components.
- Co-locate a component's tests (`Component.test.tsx`) next to `Component.tsx`.
- Prefer the generated API client in `web/src/api/` over hand-written `fetch` calls — regenerate it with `npm run generate:api` after changing a Go service's OpenAPI spec, never hand-edit it.

## Testing

- Test behavior through public interfaces, not implementation details.
- Use table-driven tests for exhaustive input coverage (Go) and `it.each` (TypeScript).
- Integration tests that need a real database spin up instances in Docker via `testcontainers-go` / `testcontainers` (TS).
- Every public function/exported component that handles external input must have at least one test.

## Architecture

- Go services and the TypeScript frontend each have their own build/lint/test entry points (`make verify` for Go, `npm run check` for `web/`) — there is no single combined command, so a change touching both must satisfy both.
- The OpenAPI spec in `api/openapi.yaml` is the source of truth for the Go↔TypeScript contract; regenerate both server stubs and the TS client from it rather than editing generated code by hand.
