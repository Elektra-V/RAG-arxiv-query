#!/bin/bash
# Script to change git remote and rewrite commit history with work identity

set -e  # Exit on error

# Configuration - EDIT THESE VALUES
WORK_NAME="YOUR_WORK_NAME"
WORK_EMAIL="your.work.email@company.com"
NEW_REPO_URL="https://github.com/company/rag-query.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Git Remote Change Script ===${NC}\n"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "rag_api" ]; then
    echo -e "${RED}Error: Must be run from rag-api directory${NC}"
    exit 1
fi

# Step 1: Backup
echo -e "${YELLOW}Step 1: Creating backup...${NC}"
cd ..
if [ -d "rag-api-backup" ]; then
    echo -e "${YELLOW}Backup already exists, skipping...${NC}"
else
    cp -r rag-api rag-api-backup
    echo -e "${GREEN}Backup created at: $(pwd)/rag-api-backup${NC}"
fi
cd rag-api

# Step 2: Show current remote
echo -e "\n${YELLOW}Step 2: Current remote configuration:${NC}"
git remote -v
echo ""

# Step 3: Remove old remote
echo -e "${YELLOW}Step 3: Removing old remote...${NC}"
if git remote get-url origin &>/dev/null; then
    git remote remove origin
    echo -e "${GREEN}Old remote removed${NC}"
else
    echo -e "${YELLOW}No origin remote found${NC}"
fi

# Step 4: Set work identity
echo -e "\n${YELLOW}Step 4: Setting work identity...${NC}"
git config user.name "$WORK_NAME"
git config user.email "$WORK_EMAIL"
echo -e "${GREEN}Identity set to: $WORK_NAME <$WORK_EMAIL>${NC}"

# Step 5: Rewrite commit history
echo -e "\n${YELLOW}Step 5: Rewriting commit history...${NC}"
echo -e "${YELLOW}This may take a moment...${NC}"

git filter-branch --env-filter "
export GIT_AUTHOR_NAME=\"$WORK_NAME\"
export GIT_AUTHOR_EMAIL=\"$WORK_EMAIL\"
export GIT_COMMITTER_NAME=\"$WORK_NAME\"
export GIT_COMMITTER_EMAIL=\"$WORK_EMAIL\"
" --tag-name-filter cat -- --branches --tags

# Step 6: Clean up backup refs
echo -e "\n${YELLOW}Step 6: Cleaning up backup references...${NC}"
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d 2>/dev/null || true
echo -e "${GREEN}Cleanup complete${NC}"

# Step 7: Add new remote
echo -e "\n${YELLOW}Step 7: Adding new remote...${NC}"
git remote add origin "$NEW_REPO_URL"
echo -e "${GREEN}New remote added: $NEW_REPO_URL${NC}"

# Step 8: Verify commits
echo -e "\n${YELLOW}Step 8: Verifying rewritten commits...${NC}"
echo -e "${GREEN}Recent commits:${NC}"
git log --pretty=format:"%h | %an | %ae | %s" | head -10

# Step 9: Confirm before pushing
echo -e "\n${YELLOW}Step 9: Ready to push${NC}"
echo -e "${RED}WARNING: This will force push to the new repository!${NC}"
read -p "Do you want to push now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Pushing to new repository...${NC}"
    git push -u origin main --force
    echo -e "\n${GREEN}✓ Successfully pushed to new repository!${NC}"
else
    echo -e "${YELLOW}Push cancelled. Run manually with:${NC}"
    echo -e "  ${GREEN}git push -u origin main --force${NC}"
fi

echo -e "\n${GREEN}=== Script Complete ===${NC}"
echo -e "Backup location: $(cd .. && pwd)/rag-api-backup"

