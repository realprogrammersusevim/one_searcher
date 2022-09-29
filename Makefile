main: main.py
	pyinstaller --onefile --noconfirm --clean main.py

clean:
	rm -rf build dist

.PHONY: clean all
