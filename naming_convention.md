# Naming Conventions

Per garantire di qualità dello sviluppo del codice verranno usati i seguenti criteri:

---

## Backend (Python / Flask)

| Costrutto | Stile | Esempio |
|---|---|---|
| Variabili e attributi | `snake_case` | `device_list`, `asset_id` |
| Funzioni e metodi | `snake_case` | `get_device_list()`, `save_assessment()` |
| Classi ed Entity | `PascalCase` | `Device`, `Asset`, `AssessmentRequirement` |
| Data Transfer Object (DTO) | `PascalCase` + suffisso `DTO` | `CreateDeviceDTO`, `ModifyAssetDTO` |
| Interfacce (Porte) | `PascalCase` + prefisso `Interface` | `InterfaceDeviceRepository`, `InterfaceDeviceUseCase` |
| Costanti di modulo | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| Attributi e metodi privati | `snake_case` + prefisso `_` | `_repository`, `_validate_business_rules()` |


## Frontend (JavaScript / Vue.js)

| Costrutto | Stile | Esempio |
|---|---|---|
| Variabili e attributi | `camelCase` | `deviceList`, `isLoading` |
| Funzioni e metodi | `camelCase` | `getDeviceList()`, `saveAssessment()` |
| Handler di eventi | `camelCase` + prefisso `handle` | `handleSubmit()`, `handleDelete()` |
| Componenti Vue (file) | `PascalCase` | `DeviceCard.vue`, `AssessmentTree.vue` |
| Store Pinia | `camelCase` + prefisso `use` + suffisso `Store` | `useDeviceStore`, `useAssessmentStore` |

## Persistenza (MongoDB)

| Costrutto | Stile | Esempio |
|---|---|---|
| Campi dei documenti | `snake_case` | `device_name`, `asset_list` |
| Nomi delle collection | `lowercase` al plurale | `devices`, `models` |

## Indentazione

I blocchi annidati devono seguire un'indentazione equivalente a **2 spazi**, sia nel Backend che nel Frontend.