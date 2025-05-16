from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-memgraph")

# Initialize FastMCP server
mcp = FastMCP("mcp-memgraph")

# Configuration from environment variables with defaults
MEMGRAPH_URI = os.getenv("MEMGRAPH_URI", "bolt://localhost:7687")
MEMGRAPH_USER = os.getenv("MEMGRAPH_USER", "")
MEMGRAPH_PASSWORD = os.getenv("MEMGRAPH_PASSWORD", "")

# Only create the driver if we're not in the main module yet
driver = None

def get_driver():
    """Get or create the Neo4j driver with lazy initialization"""
    global driver
    if driver is None:
        driver = GraphDatabase.driver(MEMGRAPH_URI, auth=(MEMGRAPH_USER, MEMGRAPH_PASSWORD))
    return driver

def execute_query(query):
    """Helper function to execute a query on Memgraph"""
    with get_driver().session() as session:
        return session.run(query).data()

@mcp.tool()
def run_query(query: str) -> list:
    """Run a query against Memgraph"""
    logger.info(f"Running query: {query}")
    try:
        result = execute_query(query)
        return result
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        return [f"Error: {str(e)}"]

@mcp.resource("schema://main")
def get_schema() -> str:
    """Get Memgraph schema information as a resource"""
    logger.info("Fetching Memgraph schema...")
    try:
        with get_driver().session() as session:
            return session.run("SHOW SCHEMA INFO").data()
    except Exception as e:
        logger.error(f"Schema fetch failed: {str(e)}")
        return f"Error fetching schema: {str(e)}"

if __name__ == "__main__":
    # Log configuration for debugging
    logger.info(f"Memgraph MCP Server Configuration:")
    logger.info(f"  URI: {MEMGRAPH_URI}")
    logger.info(f"  User: {MEMGRAPH_USER}")
    logger.info(f"  Password: {'*' * len(MEMGRAPH_PASSWORD) if MEMGRAPH_PASSWORD else '(not set)'}")
    
    # Initialize and run the server
    logger.info("Starting FastMCP server...")
    mcp.run(transport="stdio")
