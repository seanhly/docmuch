build:
	(echo '#!/usr/bin/env python' && (cd src && zip -r - * 2>/dev/null | cat)) > docmuch && chmod 755 docmuch
install: build
	sudo mv docmuch /usr/bin/; sudo chown root:root /usr/bin/docmuch
