#!/usr/bin/env python3
"""
Basit Render Deployment Script
"""

import subprocess
import json

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    print("🚀 Render Deployment Başlatılıyor...")

    # GitHub'a push
    print("📤 GitHub'a push yapılıyor...")
    success, out, err = run_cmd('git add . && git commit -m "Render deploy ready" && git push origin master')

    if success:
        print("✅ GitHub push başarılı")

        # Deploy bilgileri
        deploy_info = {
            "github_repo": "https://github.com/Schelebi/otto-platform",
            "render_url": "https://render.com/deploy",
            "expected_api": "https://otto-api.onrender.com",
            "steps": [
                "1. https://render.com'a git",
                "2. GitHub ile giriş yap",
                "3. New Web Service → GitHub'dan Schelebi/otto-platform seç",
                "4. render.yaml dosyasını otomatik algıla",
                "5. Deploy butonuna tıkla",
                "6. Deploy tamamlandığında URL'yi kopyala"
            ]
        }

        with open("render_deploy_info.json", "w") as f:
            json.dump(deploy_info, f, indent=2, ensure_ascii=False)

        print("📋 Deploy bilgileri oluşturuldu: render_deploy_info.json")
        print(f"🌐 Beklenen API URL: {deploy_info['expected_api']}")

        # Manuel deploy talimatları
        print("\n🎯 RENDER DEPLOY TALİMATLARI:")
        for step in deploy_info['steps']:
            print(f"   {step}")

        print("\n✅ Hazır! Render'a deploy edebilirsiniz.")

    else:
        print(f"❌ Hata: {err}")

if __name__ == "__main__":
    main()
