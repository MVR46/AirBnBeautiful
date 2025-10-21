#!/bin/bash

# Test script to verify backend API is working correctly
# Tests all endpoints with sample data

set -e  # Exit on error

API_BASE="http://localhost:8000"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   API Connection Test Suite                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to test an endpoint
test_endpoint() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_BASE$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_BASE$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    
    echo "HTTP Status: $http_code"
    
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        echo "Response preview: $(echo "$body" | head -c 200)..."
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Response: $body"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    echo ""
}

# Check if backend is running
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Checking Backend Connection..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if ! curl -s "$API_BASE" > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend is not running!${NC}"
    echo ""
    echo "Please start the backend first:"
    echo "  cd backend && ./start.sh"
    echo ""
    echo "Or use the combined start script:"
    echo "  ./scripts/start-all.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Backend is running at $API_BASE${NC}"
echo ""

# ===== Test Health Check =====
test_endpoint \
    "Health Check (GET /)" \
    "GET" \
    "/" \
    ""

# ===== Test Search Endpoint =====
test_endpoint \
    "NLP Search (POST /search)" \
    "POST" \
    "/search" \
    '{"query": "2 guests in Centro with wifi"}'

# ===== Test Listings Endpoint =====
# First, get a listing ID from search results
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Getting sample listing ID..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SEARCH_RESPONSE=$(curl -s -X POST "$API_BASE/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "apartment in Madrid"}')

LISTING_ID=$(echo "$SEARCH_RESPONSE" | grep -o '"id":"[^"]*"' | head -n 1 | cut -d'"' -f4)

if [ -z "$LISTING_ID" ]; then
    echo -e "${YELLOW}⚠ Could not get listing ID, skipping listing detail test${NC}"
    echo ""
else
    echo "Sample Listing ID: $LISTING_ID"
    echo ""
    
    test_endpoint \
        "Get Listing Detail (GET /listings/{id})" \
        "GET" \
        "/listings/$LISTING_ID" \
        ""
fi

# ===== Test Neighborhood Chat =====
if [ ! -z "$LISTING_ID" ]; then
    test_endpoint \
        "Neighborhood Chat (POST /neighborhood-chat)" \
        "POST" \
        "/neighborhood-chat" \
        "{\"listingId\": \"$LISTING_ID\", \"message\": \"Tell me about this neighborhood\"}"
else
    echo -e "${YELLOW}⚠ Skipping neighborhood chat test (no listing ID)${NC}"
    echo ""
fi

# ===== Test Landlord Endpoints =====
test_endpoint \
    "Landlord Prefill (GET /landlord/prefill)" \
    "GET" \
    "/landlord/prefill" \
    ""

test_endpoint \
    "Amenities from Images (POST /landlord/amenities-from-images)" \
    "POST" \
    "/landlord/amenities-from-images" \
    '{"photoIds": ["p1", "p2"]}'

test_endpoint \
    "Price Suggestions (POST /landlord/price-suggestions)" \
    "POST" \
    "/landlord/price-suggestions" \
    '{"currentAmenities": ["WiFi", "Kitchen"], "targetPrice": 120, "listingMeta": {"guests": 2, "beds": 1, "baths": 1.0, "neighborhood": "Centro"}}'

# ===== Summary =====
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All $TOTAL_TESTS tests passed!${NC}"
    echo ""
    echo "The backend API is working correctly."
    echo "Frontend should be able to connect successfully."
else
    echo -e "${RED}❌ $TESTS_FAILED of $TOTAL_TESTS tests failed${NC}"
    echo -e "${GREEN}✓ $TESTS_PASSED tests passed${NC}"
    echo ""
    echo "Please check the error messages above."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Exit with failure code if any tests failed
if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
fi

