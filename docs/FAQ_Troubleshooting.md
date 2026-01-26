# FAQ & Troubleshooting

## Frequently Asked Questions

### Is my data safe?
Yes. OpenYuGi is a **local-first** application. All your data is stored in JSON files in the `data/` directory. We do not upload your collection to any cloud server.

### Can I run this on a Raspberry Pi?
Yes, provided you can install Python 3.10+ and the required dependencies (OpenCV, etc.). Performance of the AI scanner might be limited on older models.

### How do I backup my collection?
Simply copy the `data/` folder to a safe location (e.g., an external drive or cloud storage folder).

---

## Troubleshooting

### Scanner Issues

#### "Scanner dependencies not found"
The scanner requires specific Python libraries to function. Ensure you have installed them:
```bash
pip install -r requirements.txt
```
**Note**: OpenYuGi uses **YOLOv8** and **EasyOCR/DocTR**. It does **NOT** use Tesseract. You do not need to install Tesseract.

#### "Live Scan" is black / Camera not working
1. Check if your browser/OS has granted camera permissions to the terminal or browser running the app.
2. Ensure no other application (Zoom, Discord) is using the camera.
3. Try refreshing the page.
4. If using `localhost`, some browsers block camera access on non-secure (HTTP) contexts unless explicitly allowed.

#### The Scanner isn't detecting my cards
- Ensure the card is fully visible and placed on a contrasting background (e.g., a dark playmat).
- Use the **Capture & Scan** button. The app does not currently support "continuous auto-scan" to save resources; it processes the frame you capture.

### Data & Images

#### "Images are missing"
OpenYuGi downloads card images on-demand to save disk space.
1. Ensure you have an active internet connection.
2. Check `data/images` folder permissions.
3. You can force a download of all images in **Settings > Download All Images**.

#### "PermissionError" or "Access Denied" when saving
This often happens on **Windows** if:
- You have the `.json` file open in a text editor (like Notepad++ or VS Code).
- A cloud sync service (OneDrive, Dropbox) is locking the file to sync it.
- An antivirus is scanning the file.

**Solution**: Close any external programs using the file and try again. The app has a built-in retry mechanism, but persistent locks will cause saves to fail.

#### App crashes on startup
Check the console output. Common causes:
- **Port 8080 in use**: Another app is using the default port.
- **Corrupt Config**: Delete `data/config.json` to reset settings.

### Advanced Debugging

#### Enabling Debug Mode
If you are developing or facing complex issues, you can enable the **Debug Lab** in the Scan tab. This provides a visual breakdown of the pipeline (Crop -> OCR -> Match).
