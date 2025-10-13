#!/usr/bin/env python3
"""
Script to fix FastAPI endpoint dependencies by moving Depends(require_role(...)) 
from function arguments to route decorator dependencies.

This resolves lint errors about function calls in argument defaults.
"""

import re
from pathlib import Path

def fix_backend_dependencies():
    """Fix all FastAPI endpoints with Depends(require_role(...)) in arguments"""
    
    backend_file = Path("backend/backend.py")
    if not backend_file.exists():
        print(f"Error: {backend_file} not found")
        return False
    
    # Read the current content
    content = backend_file.read_text(encoding='utf-8')
    
    # Define the patterns and replacements
    fixes = [
        # /api/ask endpoint
        {
            'pattern': r'@app\.post\("/api/ask"\)\nasync def api_ask\(request: AskRequest, user=Depends\(require_role\("user"\)\)\):',
            'replacement': '@app.post("/api/ask", dependencies=[Depends(require_role("user"))])\nasync def api_ask(request: AskRequest):'
        },
        
        # /ask endpoint
        {
            'pattern': r'@app\.post\("/ask"\)  # type: ignore\nasync def ask\(request: AskRequest, user=Depends\(require_role\("user"\)\)\):',
            'replacement': '@app.post("/ask", dependencies=[Depends(require_role("user"))])  # type: ignore\nasync def ask(request: AskRequest):'
        },
        
        # /api/scan_vault endpoint
        {
            'pattern': r'@app\.post\("/api/scan_vault"\)\nasync def scan_vault\(request: ScanVaultRequest, user=Depends\(require_role\("admin"\)\)\):',
            'replacement': '@app.post("/api/scan_vault", dependencies=[Depends(require_role("admin"))])\nasync def scan_vault(request: ScanVaultRequest):'
        },
        
        # /api/web endpoint
        {
            'pattern': r'@app\.post\("/api/web"\)\nasync def api_web\(request: WebRequest, user=Depends\(require_role\("user"\)\)\):',
            'replacement': '@app.post("/api/web", dependencies=[Depends(require_role("user"))])\nasync def api_web(request: WebRequest):'
        },
        
        # /web endpoint
        {
            'pattern': r'@app\.post\("/web"\)\nasync def web\(request: WebRequest, user=Depends\(require_role\("user"\)\)\):',
            'replacement': '@app.post("/web", dependencies=[Depends(require_role("user"))])\nasync def web(request: WebRequest):'
        },
        
        # /api/reindex endpoint
        {
            'pattern': r'@app\.post\("/api/reindex"\)\nasync def api_reindex\(request: ReindexRequest, user=Depends\(require_role\("admin"\)\)\):',
            'replacement': '@app.post("/api/reindex", dependencies=[Depends(require_role("admin"))])\nasync def api_reindex(request: ReindexRequest):'
        },
        
        # /reindex endpoint
        {
            'pattern': r'@app\.post\("/reindex"\)\nasync def reindex\(request: ReindexRequest, user=Depends\(require_role\("admin"\)\)\):',
            'replacement': '@app.post("/reindex", dependencies=[Depends(require_role("admin"))])\nasync def reindex(request: ReindexRequest):'
        },
        
        # /transcribe endpoint
        {
            'pattern': r'@app\.post\("/transcribe"\)\nasync def transcribe_audio\(request: TranscribeRequest, user=Depends\(require_role\("user"\)\)\):',
            'replacement': '@app.post("/transcribe", dependencies=[Depends(require_role("user"))])\nasync def transcribe_audio(request: TranscribeRequest):'
        },
        
        # /api/search endpoint
        {
            'pattern': r'@app\.post\("/api/search"\)\nasync def search\(query: str, top_k: int = 5, user=Depends\(require_role\("user"\)\)\):',
            'replacement': '@app.post("/api/search", dependencies=[Depends(require_role("user"))])\nasync def search(query: str, top_k: int = 5):'
        },
        
        # /api/index_pdf endpoint
        {
            'pattern': r'@app\.post\("/api/index_pdf"\)\nasync def index_pdf\(pdf_path: str, user=Depends\(require_role\("admin"\)\)\):',
            'replacement': '@app.post("/api/index_pdf", dependencies=[Depends(require_role("admin"))])\nasync def index_pdf(pdf_path: str):'
        },
        
        # Enterprise endpoints (if present)
        {
            'pattern': r'async def enterprise_status\(user=Depends\(require_role\("admin"\)\)\):',
            'replacement': 'async def enterprise_status():'
        },
        {
            'pattern': r'@app\.get\("/api/enterprise/status"\)\n    async def enterprise_status\(\):',
            'replacement': '@app.get("/api/enterprise/status", dependencies=[Depends(require_role("admin"))])\n    async def enterprise_status():'
        },
        
        {
            'pattern': r'async def enterprise_demo\(user=Depends\(require_role\("admin"\)\)\):',
            'replacement': 'async def enterprise_demo():'
        },
        {
            'pattern': r'@app\.get\("/api/enterprise/demo"\)\n    async def enterprise_demo\(\):',
            'replacement': '@app.get("/api/enterprise/demo", dependencies=[Depends(require_role("admin"))])\n    async def enterprise_demo():'
        }
    ]
    
    # Apply all fixes
    modified = False
    for fix in fixes:
        pattern = fix['pattern']
        replacement = fix['replacement']
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
            print(f"✓ Fixed pattern: {pattern[:50]}...")
        else:
            print(f"- Pattern not found: {pattern[:50]}...")
    
    # Handle enterprise endpoints with conditional fix
    if 'async def enterprise_status(user=Depends(require_role("admin"))):' in content:
        # Fix the enterprise status endpoint decorator
        content = re.sub(
            r'@app\.get\("/api/enterprise/status"\)\s+async def enterprise_status\(user=Depends\(require_role\("admin"\)\)\):',
            '@app.get("/api/enterprise/status", dependencies=[Depends(require_role("admin"))])\n    async def enterprise_status():',
            content
        )
        modified = True
        print("✓ Fixed enterprise_status endpoint")
    
    if 'async def enterprise_demo(user=Depends(require_role("admin"))):' in content:
        # Fix the enterprise demo endpoint decorator
        content = re.sub(
            r'@app\.get\("/api/enterprise/demo"\)\s+async def enterprise_demo\(user=Depends\(require_role\("admin"\)\)\):',
            '@app.get("/api/enterprise/demo", dependencies=[Depends(require_role("admin"))])\n    async def enterprise_demo():',
            content
        )
        modified = True
        print("✓ Fixed enterprise_demo endpoint")
    
    if modified:
        # Write the fixed content back
        backend_file.write_text(content, encoding='utf-8')
        print(f"\n✅ Successfully updated {backend_file}")
        print("All FastAPI endpoints now use dependencies in route decorators instead of function arguments.")
        return True
    else:
        print(f"\n⚠️  No changes needed in {backend_file}")
        return False

def main():
    """Main function to run the dependency fixes"""
    print("🔧 Fixing FastAPI endpoint dependencies...")
    print("=" * 60)
    
    success = fix_backend_dependencies()
    
    if success:
        print("\n🎉 Dependency fixes completed successfully!")
        print("\nNext steps:")
        print("1. Test the backend to ensure all endpoints still work")
        print("2. Run linting to verify errors are resolved")
        print("3. Continue with the next security hardening task")
    else:
        print("\n❌ No fixes were applied. Check if the patterns match your code.")

if __name__ == "__main__":
    main()