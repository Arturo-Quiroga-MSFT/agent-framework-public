#!/usr/bin/env python3
"""
Azure ML Studio Connectivity Diagnostic Script

This script tests various Azure ML endpoints to help diagnose connectivity issues.
Error 530 typically indicates a Cloudflare origin error - the request reached 
Cloudflare but the origin server (Azure) didn't respond.

Common causes of Error 530:
1. DNS resolution issues
2. Network/firewall blocking connections
3. Regional service outage
4. Authentication/tenant configuration issues
5. VPN/Proxy interference
"""

import os
import sys
import socket
import time
import json
from datetime import datetime
from urllib.parse import urlparse

# Try to import requests, provide guidance if not available
try:
    import requests
except ImportError:
    print("❌ 'requests' module not found. Install with: pip install requests")
    sys.exit(1)

# Optional: DNS resolution details
try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(test: str, success: bool, details: str = ""):
    icon = "✅" if success else "❌"
    print(f"{icon} {test}")
    if details:
        for line in details.split('\n'):
            print(f"   {line}")


def test_dns_resolution(hostname: str) -> dict:
    """Test DNS resolution for a hostname."""
    result = {"success": False, "ips": [], "error": None}
    
    try:
        # Standard socket resolution
        ips = socket.gethostbyname_ex(hostname)[2]
        result["ips"] = ips
        result["success"] = True
        
        # Try detailed DNS if available
        if HAS_DNS:
            try:
                answers = dns.resolver.resolve(hostname, 'A')
                result["dns_records"] = [str(r) for r in answers]
            except Exception:
                pass
                
    except socket.gaierror as e:
        result["error"] = str(e)
    except Exception as e:
        result["error"] = str(e)
    
    return result


def test_https_connectivity(url: str, timeout: int = 10) -> dict:
    """Test HTTPS connectivity to a URL."""
    result = {
        "success": False,
        "status_code": None,
        "response_time_ms": None,
        "headers": {},
        "error": None,
        "cloudflare": False
    }
    
    try:
        start = time.time()
        response = requests.get(
            url, 
            timeout=timeout,
            allow_redirects=True,
            headers={
                "User-Agent": "AzureML-Diagnostic/1.0",
                "Accept": "text/html,application/json"
            }
        )
        elapsed = (time.time() - start) * 1000
        
        result["status_code"] = response.status_code
        result["response_time_ms"] = round(elapsed, 2)
        result["success"] = response.status_code < 400
        result["final_url"] = response.url
        
        # Check for Cloudflare headers
        cf_headers = ["cf-ray", "cf-cache-status", "server"]
        for h in cf_headers:
            if h in response.headers:
                result["headers"][h] = response.headers[h]
                if "cloudflare" in response.headers.get("server", "").lower():
                    result["cloudflare"] = True
        
        # Check for error body
        if response.status_code >= 400:
            try:
                result["error_body"] = response.json()
            except:
                result["error_body"] = response.text[:500]
                
    except requests.exceptions.Timeout:
        result["error"] = "Connection timed out"
    except requests.exceptions.SSLError as e:
        result["error"] = f"SSL Error: {str(e)[:100]}"
    except requests.exceptions.ConnectionError as e:
        result["error"] = f"Connection Error: {str(e)[:100]}"
    except Exception as e:
        result["error"] = str(e)[:100]
    
    return result


def test_azure_auth_endpoint() -> dict:
    """Test Azure AD authentication endpoint."""
    url = "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
    return test_https_connectivity(url)


def get_network_info() -> dict:
    """Get basic network information."""
    info = {
        "hostname": socket.gethostname(),
        "external_ip": None,
        "location": None
    }
    
    try:
        # Get external IP
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        if response.status_code == 200:
            info["external_ip"] = response.json().get("ip")
            
        # Get location info
        if info["external_ip"]:
            geo = requests.get(f"https://ipapi.co/{info['external_ip']}/json/", timeout=5)
            if geo.status_code == 200:
                data = geo.json()
                info["location"] = f"{data.get('city', 'Unknown')}, {data.get('country_name', 'Unknown')}"
                info["isp"] = data.get("org", "Unknown")
    except:
        pass
    
    return info


def run_diagnostics():
    """Run full Azure ML connectivity diagnostics."""
    
    print_header("Azure ML Studio Connectivity Diagnostics")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python: {sys.version.split()[0]}")
    
    # Network info
    print_header("Network Information")
    net_info = get_network_info()
    print(f"Hostname: {net_info['hostname']}")
    print(f"External IP: {net_info.get('external_ip', 'Unable to detect')}")
    print(f"Location: {net_info.get('location', 'Unable to detect')}")
    print(f"ISP: {net_info.get('isp', 'Unable to detect')}")
    
    # Endpoints to test
    endpoints = [
        ("Azure ML Studio", "https://ml.azure.com"),
        ("Azure ML API", "https://ml.azure.com/api/health"),
        ("Azure Portal", "https://portal.azure.com"),
        ("Azure Login", "https://login.microsoftonline.com"),
        ("Azure Management", "https://management.azure.com"),
    ]
    
    # DNS Tests
    print_header("DNS Resolution Tests")
    for name, url in endpoints:
        hostname = urlparse(url).netloc
        dns_result = test_dns_resolution(hostname)
        if dns_result["success"]:
            print_result(
                f"{hostname}",
                True,
                f"Resolved to: {', '.join(dns_result['ips'][:3])}"
            )
        else:
            print_result(f"{hostname}", False, f"Error: {dns_result['error']}")
    
    # HTTPS Connectivity Tests
    print_header("HTTPS Connectivity Tests")
    results = {}
    
    for name, url in endpoints:
        print(f"\nTesting: {name} ({url})")
        result = test_https_connectivity(url)
        results[name] = result
        
        if result["success"]:
            details = f"Status: {result['status_code']} | Time: {result['response_time_ms']}ms"
            if result.get("cloudflare"):
                details += " | Via Cloudflare"
            print_result(name, True, details)
        else:
            error_msg = f"Status: {result.get('status_code', 'N/A')}"
            if result.get("error"):
                error_msg += f"\nError: {result['error']}"
            if result.get("error_body"):
                error_msg += f"\nBody: {json.dumps(result['error_body'], indent=2)[:200]}"
            print_result(name, False, error_msg)
    
    # Azure AD Auth Test
    print_header("Azure AD Authentication Endpoint")
    auth_result = test_azure_auth_endpoint()
    if auth_result["success"]:
        print_result("Azure AD OpenID Config", True, f"Status: {auth_result['status_code']}")
    else:
        print_result("Azure AD OpenID Config", False, auth_result.get("error", "Failed"))
    
    # Summary and Recommendations
    print_header("Diagnosis Summary")
    
    failed = [name for name, result in results.items() if not result["success"]]
    
    if not failed:
        print("✅ All connectivity tests PASSED")
        print("\nIf your colleague is getting Error 530, the issue is likely:")
        print("  • Their specific network/ISP blocking Azure")
        print("  • VPN or proxy interference")
        print("  • Corporate firewall rules")
        print("  • Regional DNS issues")
        print("  • Browser cache/cookies issue")
    else:
        print(f"❌ {len(failed)} test(s) FAILED: {', '.join(failed)}")
        
    print_header("Error 530 Troubleshooting Steps")
    print("""
For Error 530 (Cloudflare Origin Error):

1. CLEAR BROWSER DATA
   • Clear cookies and cache for ml.azure.com
   • Try incognito/private browsing mode

2. CHECK DNS
   • Try using Google DNS (8.8.8.8) or Cloudflare DNS (1.1.1.1)
   • Flush DNS cache: 
     - Windows: ipconfig /flushdns
     - macOS: sudo dscacheutil -flushcache

3. NETWORK ISSUES
   • Disable VPN temporarily
   • Try a different network (mobile hotspot)
   • Check if corporate firewall blocks Azure

4. BROWSER ISSUES  
   • Try a different browser
   • Disable browser extensions
   • Check for HTTPS inspection/proxy

5. AZURE STATUS
   • Check Azure Status: https://status.azure.com
   • Check for regional outages

6. SHARE THIS SCRIPT
   • Have your colleague run this script
   • Compare results to identify differences
""")
    
    # Export results
    output_file = "azure_ml_diagnostic_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "network": net_info,
            "results": results
        }, f, indent=2, default=str)
    print(f"\n📄 Results saved to: {output_file}")


if __name__ == "__main__":
    run_diagnostics()
