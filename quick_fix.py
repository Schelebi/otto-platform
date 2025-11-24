#!/usr/bin/env python3
import subprocess
import os

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    print("🔧 HIZLI VERCEL FIX")

    # 1. Environment değişkenini kaldır
    print("1. Eski env kaldırılıyor...")
    run_cmd('echo yes | npx vercel env rm VITE_API_BASE_URL production')

    # 2. Yeni environment değişkeni ekle
    print("2. Yeni env ekleniyor...")
    run_cmd('echo "https://ottomans.onrender.com" | npx vercel env add VITE_API_BASE_URL production')

    # 3. Local .env güncelle
    print("3. Local .env güncelleniyor...")
    env_content = """VITE_API_BASE_URL=https://ottomans.onrender.com
DB_HOST=35.214.224.135
DB_USER=uwcw1gm1sor8u
DB_PASSWORD=g05jkizfzjdp
DB_NAME=db6ctx4kvleywe
NODE_ENV=production"""

    try:
        os.chmod(".env", 0o666)
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env güncellendi")
    except:
        print("⚠️ .env güncellenemedi")

    # 4. Deploy
    print("4. Deploy başlatılıyor...")
    success, stdout, stderr = run_cmd("npx vercel --prod")

    if success:
        print("✅ Deploy başarılı!")
        for line in stdout.split('\n'):
            if 'https://' in line and 'vercel.app' in line:
                print(f"🌐 URL: {line.strip()}")
    else:
        print("❌ Deploy başarısız")

if __name__ == "__main__":
    main()
