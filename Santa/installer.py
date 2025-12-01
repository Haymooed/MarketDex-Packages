import os, shutil, tempfile, zipfile, urllib.request

ZIP_URL = "https://github.com/Haymooed/SantaDaily/archive/refs/heads/main.zip"
PACKAGE_NAME = "santadaily"
TARGET = "ballsde​x/packages"

async def install_santa(bot, ctx):
    await ctx.send("📥 Downloading Santa Daily…")

    tmp = tempfile.mkdtemp()
    zip_path = os.path.join(tmp, "santa.zip")
    urllib.request.urlretrieve(ZIP_URL, zip_path)

    await ctx.send("📦 Extracting…")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(tmp)

    root = next(
        os.path.join(tmp, d)
        for d in os.listdir(tmp)
        if os.path.isdir(os.path.join(tmp, d))
    )
    src = os.path.join(root, PACKAGE_NAME)
    dst = os.path.join(TARGET, PACKAGE_NAME)

    if not os.path.isdir(src):
        await ctx.send("❌ Package folder missing.")
        return

    if os.path.exists(dst):
        await ctx.send("🗑 Removing old version…")
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
    shutil.rmtree(tmp)

    await ctx.send("🎄 Santa Daily installed! Restart the bot.")
