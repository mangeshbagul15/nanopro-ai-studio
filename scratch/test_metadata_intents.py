import os
import sys
sys.path.insert(0, os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')

from app.agents.extended_intents import handle_extended_intents

prompts = [
    # 1. Master prompt from user
    "tyala na ek as modify karati pahile tyane sagle db check karun to konta db ahe oracle ki snowflake ki postgres ki sqllight then db konte ahet tyanche exact db namme db kiti konte ka banavlet te schema konta ahe schemache exact name kayahet kiti ahet schema db madhe konte and kiti tables ahet and ka banavlet te table madhe konte column ahet kiti ahet data type kay ahe sagla table baddal mahit asav full info tyachya kade adhich asavi kiti count ahe nakki ka andkuthe kuthe ha table use karu shakto join kontya kontya table la possible ahe pk and fk konte columns ahet db to db connection vyayla pahije ek db madhala table and dusrya db madhala table match karun final report banavnya sathi je lagel te sagal. tables madhuna as per logic report banaun and summery pn tyane dyavi means adhich tyachya kade details havi and new activity db table name jhami tr te pn tyacyhya kade modify jhal pahije automaticaly tyala purn structure, atchitecture, flow sagl mahit pahije magach to correct chat nad fast correct answer karen",
    # 2. SQL query generation prompt from previous turn
    "ek table ahe ACCOUNTS to BANK_DB chya L0 layer madhe ahe so tya table che first 5 record fetch karun pahujet so procide SQL query for snowflake",
    # 3. Cross-DB match and report
    "ek db madhala table and dusrya db madhala table match karun final report banavnya sathi",
    # 4. Table structure and column datatypes
    "table madhe konte column ahet kiti ahet data type kay ahe sagla table baddal mahit asav",
    # 5. CUSTOMERS table details
    "CUSTOMERS table baddal mahit sanga columns and pk fk kay ahet",
    # 6. Actual DB name
    "actual database is BANK_DB"
]

for idx, p in enumerate(prompts, 1):
    p_lower = p.lower().strip()
    res = handle_extended_intents(p_lower, p)
    handled = res.get('handled') if res else False
    agent = res.get('agent_id') if res else None
    reply = res.get('reply', '') if res else ''
    print(f"Test {idx}: Handled={handled} | Agent={agent} | ReplyLen={len(reply)}")
    print("Preview:", reply[:150].replace('\n', ' '))
    print("-" * 60)
