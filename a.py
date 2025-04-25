with open("credentials.json", "r") as f:
    raw = f.read().replace("\n", "\\n")

with open("env_ready_credentials.txt", "w") as out:
    out.write(raw)

print("✅ Đã ghi ra env_ready_credentials.txt!")
input("Bấm Enter để thoát...")
