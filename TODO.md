# Filename Display - UX Enhancement

**Approved:** Show "Selected: filename.ext" below Choose File button.

## ✅ Completed
- [x] Removed auto-convert ✓ Manual click only
- [x] Servers stable, API working (200 OK logs)

## ✅ Completed: Filename Display Added
```
📁 Choose File
Selected: myfile.usr  ← Green pill style
```
- State + logic in App.jsx ✓
- `.file-name` CSS (green bg, break-all) ✓
- Clears on mode change ✓
- Vite HMR x5 (updates applied) ✓

## Final Flow
1. Click 📁 Choose File → select file
2. **"Selected: filename.ext" appears** ✓
3. Textarea fills (no auto-convert)
4. Click Convert → Output ✓

**UX Perfect.** All requests done: manual convert + filename visible.

**Current Flow:** Upload → filename → textarea fills → Convert click → output
