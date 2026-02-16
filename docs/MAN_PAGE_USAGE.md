# Man Page for pptx-builder

This directory contains the manual page for `pptx-builder`.

## Viewing the Man Page

### Option 1: Using `man` command

```bash
# From the project root
man docs/pptx-builder.1
```

### Option 2: Convert to text

```bash
# Generate plain text version
man docs/pptx-builder.1 | col -b > docs/pptx-builder.txt

# Or use groff directly
groff -man -Tascii docs/pptx-builder.1 | less
```

### Option 3: Convert to PDF

```bash
# Generate PDF version
groff -man -Tps docs/pptx-builder.1 | ps2pdf - docs/pptx-builder.pdf
```

### Option 4: Convert to HTML

```bash
# Generate HTML version
groff -man -Thtml docs/pptx-builder.1 > docs/pptx-builder.html
```

## Installing System-Wide (Optional)

To install the man page system-wide (requires sudo):

```bash
# Copy to system man pages directory
sudo cp docs/pptx-builder.1 /usr/local/share/man/man1/

# Update man database
sudo mandb  # Linux
# or
sudo /usr/libexec/makewhatis /usr/local/share/man  # macOS

# Now you can use:
man pptx-builder
```

## Man Page Format

The file `pptx-builder.1` is written in **troff/groff** format, which is the standard for Unix man pages. The `.1` extension indicates it's a "User Commands" manual (section 1).

### Man Page Sections

Traditional Unix man page sections:
- **Section 1**: User commands (our file)
- **Section 2**: System calls
- **Section 3**: Library functions
- **Section 4**: Special files
- **Section 5**: File formats
- **Section 6**: Games
- **Section 7**: Miscellaneous
- **Section 8**: System administration

## Editing the Man Page

The man page uses troff markup. Common macros:

- `.TH` - Title header
- `.SH` - Section header
- `.B` - Bold text
- `.I` - Italic text
- `.TP` - Tagged paragraph
- `.nf/.fi` - No-fill mode (for code blocks)
- `.IP` - Indented paragraph
- `.RS/.RE` - Relative indent start/end

See `man 7 groff_man` for full documentation.

## Quick Reference

View the complete man page with all formatting:
```bash
man docs/pptx-builder.1
```

Search within man page (once viewing):
- `/pattern` - Search forward
- `?pattern` - Search backward
- `n` - Next match
- `N` - Previous match
- `q` - Quit
