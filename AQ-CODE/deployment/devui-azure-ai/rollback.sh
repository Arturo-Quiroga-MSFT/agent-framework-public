#!/bin/bash
# Rollback script for Azure AI Agents DevUI
# Activates a previous revision if the current deployment fails

set -e

RESOURCE_GROUP="${RESOURCE_GROUP:-rg-devui-azure-ai}"
APP_NAME="${APP_NAME:-devui-azure-ai-agents}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Azure AI Agents DevUI Rollback${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if app exists
if ! az containerapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" &>/dev/null; then
    echo -e "${RED}Error: Container App '$APP_NAME' not found in resource group '$RESOURCE_GROUP'${NC}"
    exit 1
fi

# List all revisions
echo -e "${BLUE}Available revisions:${NC}"
az containerapp revision list \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "[].{Name:name, Active:properties.active, Created:properties.createdTime, Replicas:properties.replicas, TrafficWeight:properties.trafficWeight}" \
    -o table

echo ""

# Get current active revision
CURRENT_REVISION=$(az containerapp revision list \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "[?properties.active].name | [0]" -o tsv)

echo -e "${YELLOW}Current active revision: $CURRENT_REVISION${NC}"

# Get previous active revision (second in list when sorted by creation time)
PREVIOUS_REVISION=$(az containerapp revision list \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "sort_by([], &properties.createdTime) | reverse(@) | [1].name" -o tsv)

if [ -z "$PREVIOUS_REVISION" ] || [ "$PREVIOUS_REVISION" == "null" ]; then
    echo -e "${RED}Error: No previous revision found to rollback to${NC}"
    exit 1
fi

echo -e "${BLUE}Target rollback revision: $PREVIOUS_REVISION${NC}"
echo ""

# Confirm rollback
read -p "Do you want to rollback to $PREVIOUS_REVISION? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Rollback cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Rolling back to previous revision...${NC}"

# Activate previous revision
az containerapp revision activate \
    --revision "$PREVIOUS_REVISION" \
    --resource-group "$RESOURCE_GROUP" \
    --output none

echo -e "${GREEN}✓ Rollback completed${NC}"

# Verify
sleep 5

NEW_ACTIVE=$(az containerapp revision list \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "[?properties.active].name | [0]" -o tsv)

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Rollback Successful!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo -e "${BLUE}Active revision:${NC} $NEW_ACTIVE"
echo -e "${BLUE}Previous revision:${NC} $CURRENT_REVISION (deactivated)"
echo ""
echo -e "${YELLOW}Note: The failed revision has been deactivated but not deleted.${NC}"
echo "You can delete it with:"
echo "  ${BLUE}az containerapp revision deactivate --revision $CURRENT_REVISION --resource-group $RESOURCE_GROUP${NC}"
echo ""
