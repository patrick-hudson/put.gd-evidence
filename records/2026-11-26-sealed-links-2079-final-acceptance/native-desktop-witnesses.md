# Supplemental native desktop screenshots

Every native-desktop/* PNG shows version 26.1126.7190-dev+g164e8a3af24c, gitTree f8d601a3523b16c64cb5a1cfebf3bb41fb9c54f5. Captures are actual framebuffer crops; the annotated/ directory contains the separate editor.apply rectangles/arrows. Each filename begins with the lab host and names the visible feature. These crops exclude credential input areas and unrelated old desktop notifications.

The five build diagnostics and exact agent outcomes are retained in the per-host UI JSON reports. On f44 and m74, the complete native review button and upload button are visible. d69 and Aurora review screenshots had old prior-test notification toasts overlapping the lower right corner; the recording.review and operation.seal agent outcomes nevertheless passed there. The tray row was visually witnessed and used on all five.

Session-only credentials intentionally invalidate the passed check at resident restart, as specified in the sealed-links design. On m74 and k72 a fresh Test re-established passed state, and mode On with a passphrase was accepted. m74's passphrase row is visible in m74-passphrase.png. The k72 card was partly below the fold in its restart framebuffer; the agent result confirms mode passphrase.
