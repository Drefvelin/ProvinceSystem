# Batch 13.02 — Display lib + API + storage

**Repo:** ProvinceSystem backend

1. `display.py` — defaults per kind; merge (submitted wins); validate required keys.  
2. `ALLOWED_KINDS` / `BASE_SETS`; armor `helmet_3d_tiers`.  
3. Storage: `{id}.png`+`.json`; conditional armor helmet stems; JSON ≤ 512 KiB.  
4. Approved payload includes `helmet_3d_tiers` + files.

**Done when:** curl creates all 3D kinds + mixed armor; bad display → 400.
