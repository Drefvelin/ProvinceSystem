# Batch 9.01 — Encoding fix

**Plan + build:** Stop `Â` mojibake from literal `§` under Windows javac.

**Repos:** `Workspace/armourshop`

## Plan

1. `project.build.sourceEncoding=UTF-8` in pom.  
2. Replace literal `§` in Java with `\u00A7` or ChatColor.  
3. Compile.

## Verify

- [x] Source encoding + `\u00A7` replacements done (rebuild jar on machine with local Paper deps)

