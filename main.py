from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

myEndpoint = os.getenv("PROJECT_ENDPOINT") or os.getenv("FOUNDRY_PROJECT_ENDPOINT") or ""
if not myEndpoint:
    raise RuntimeError("Set PROJECT_ENDPOINT (or FOUNDRY_PROJECT_ENDPOINT) in your .env")

def get_credential():
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    missing = [k for k,v in {
        "AZURE_TENANT_ID": tenant_id,
        "AZURE_CLIENT_ID": client_id,
        "AZURE_CLIENT_SECRET": client_secret,
    }.items() if not v]
    if missing:
        raise RuntimeError(
            f"Missing Service Principal settings: {', '.join(missing)}.\n"
            "Set them in .env (see .env.example) or environment variables."
        )
    return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

project_client = AIProjectClient(
    endpoint=myEndpoint,
    credential=get_credential(),
)

myAgent = os.getenv("AGENT_NAME", "enel-search-material")
# Get an existing agent
agent = project_client.agents.get(agent_name=myAgent)
print(f"Retrieved agent: {agent.name}")

openai_client = project_client.get_openai_client()


def get_credential():
    # Use Azure App Registration (Service Principal) only
    tenant_id = "03e8dfe4-ab90-4fdb-b851-f0128b5bd770"
    client_id = "2f85df0e-86ee-49a2-97db-70e51ddb62f6"
    client_secret = "MrD8Q~YuYRsjn1G39qcdGs3jpzY2zlhAY16dCa_t"
    missing = [k for k,v in {
        "AZURE_TENANT_ID": "03e8dfe4-ab90-4fdb-b851-f0128b5bd770",
        "AZURE_CLIENT_ID": "2f85df0e-86ee-49a2-97db-70e51ddb62f6",
        "AZURE_CLIENT_SECRET": "MrD8Q~YuYRsjn1G39qcdGs3jpzY2zlhAY16dCa_t",
    }.items() if not v]
    if missing:
        raise RuntimeError(
            f"Missing Service Principal settings: {', '.join(missing)}.\n"
            "Set them in your .env (see .env.example) or environment variables."
        )
    return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)




class DatiInput(BaseModel):
    utente: str
    messaggio: str




app = FastAPI()


@app.get("/")
async def root():
    return {"message": "online"}

@app.get("/message/{message}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.post("/send-req")
async def ricevi_messaggio(data: DatiInput):
    """
    Questo endpoint riceve un oggetto JSON, lo elabora 
    e restituisce una conferma.
    """
    
    # Qui puoi aggiungere la tua logica (es. salvare su database)
    # Reference the agent to get a response
    print("Requesting response from agent...")
    response = openai_client.responses.create(
        input=[{"role": "user", "content": f"L'utente {data.utente} ha effettuato la seguente questa richiesta {data.messaggio}"}],
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    return {
        "message": response.output_text
        }
