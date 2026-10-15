# Upload this project to GitHub

This archive contains the project source while excluding Python caches, local database files, and runtime logs.

## Windows PowerShell

1. Extract this ZIP to a folder named `GKH_AI_Resume_Analyzer_cleaned` in Downloads.
2. Clone your repository in Downloads:

```powershell
cd "$env:USERPROFILE\Downloads"
git clone https://github.com/harivel-GK/GKH-AI-RESUME-ANALYZER.git
```

3. Copy the extracted project into the cloned repository (keep the cloned `.git` folder):

```powershell
$source = "$env:USERPROFILE\Downloads\GKH_AI_Resume_Analyzer_cleaned"
$repo = "$env:USERPROFILE\Downloads\GKH-AI-RESUME-ANALYZER"
Copy-Item -Path "$source\*" -Destination $repo -Recurse -Force
Copy-Item -Path "$source\.gitignore" -Destination "$repo\.gitignore" -Force
Set-Location $repo
git add -A
git commit -m "Add AI resume analyzer project files"
git push origin main
```

If Git asks you to sign in, complete the GitHub authentication prompt. Review the files before pushing, and never commit a real `.env` file or API key.
