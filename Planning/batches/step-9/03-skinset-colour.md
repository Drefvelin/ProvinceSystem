# Batch 9.03 — SkinSet colour resolve

**Plan + build:** Load plain name + colour(s) + styles; format via TLibs.

## Plan

1. Helper: normalize `#hex` / `§c` / `&c` → hex list; apply styles.  
2. SkinSet + SkinCategory use helper (compat peel if colour missing).  

## Verify

- [x] Hex + legacy colour load  
- [ ] Multi-hex gradient works in GUI (needs jar on server)
