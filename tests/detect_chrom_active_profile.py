import os

profile_dir = "C:/Users/Biome/AppData/Local/Google/Chrome/User Data"
profiles = [f for f in os.listdir(profile_dir) if "Profile" in f or f == "Default"]

print("Available Chrome Profiles:")
for profile in profiles:
    print(f"- {profile}")

print("\nYour active profile is probably listed above. Use it in Playwright!")
