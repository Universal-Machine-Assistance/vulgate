#!/usr/bin/env python3
import sys
import os
sys.path.append('backend')
os.chdir('backend')

try:
    from app.main import app
    print('✅ App imported successfully')
    
    from app.api.api_v1.endpoints import texts
    print('✅ Texts module imported successfully')
    
    from app.services.bhagavad_gita_service import bhagavad_gita_service
    print('✅ Bhagavad Gita service imported successfully')
    
    print('✅ All imports successful!')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f'❌ Other error: {e}')
    import traceback
    traceback.print_exc() 