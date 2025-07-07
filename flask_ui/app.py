"""Flask UI application for MedAI Dossier."""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import httpx
import asyncio
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
app.config['API_BASE_URL'] = API_BASE_URL


class APIClient:
    """HTTP client for API communication."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def get_dossiers(self):
        """Get all dossiers."""
        try:
            response = await self.client.get(f"{self.base_url}/dossiers/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching dossiers: {e}")
            return []
    
    async def get_dossier(self, dossier_id: str):
        """Get specific dossier."""
        try:
            response = await self.client.get(f"{self.base_url}/dossiers/{dossier_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching dossier {dossier_id}: {e}")
            return None
    
    async def create_dossier(self, dossier_data: dict):
        """Create new dossier."""
        try:
            response = await self.client.post(f"{self.base_url}/dossiers/", json=dossier_data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error creating dossier: {e}")
            return None
    
    async def get_hta_frameworks(self):
        """Get HTA frameworks."""
        try:
            response = await self.client.get(f"{self.base_url}/hta/frameworks")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error fetching HTA frameworks: {e}")
            return {}


# Initialize API client
api_client = APIClient(API_BASE_URL)


@app.route('/')
def dashboard():
    """Dashboard with overview of dossiers."""
    try:
        # Get dossiers from API
        dossiers = asyncio.run(api_client.get_dossiers())
        
        # Calculate statistics
        stats = {
            'total_dossiers': len(dossiers),
            'draft_count': len([d for d in dossiers if d.get('status') == 'draft']),
            'in_review_count': len([d for d in dossiers if d.get('status') == 'in_review']),
            'approved_count': len([d for d in dossiers if d.get('status') == 'approved']),
            'submitted_count': len([d for d in dossiers if d.get('status') == 'submitted'])
        }
        
        return render_template('dashboard.html', dossiers=dossiers, stats=stats)
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        flash('Error loading dashboard data', 'error')
        return render_template('dashboard.html', dossiers=[], stats={})


@app.route('/dossiers')
def dossiers_list():
    """List all dossiers."""
    try:
        dossiers = asyncio.run(api_client.get_dossiers())
        return render_template('dossiers/list.html', dossiers=dossiers)
    except Exception as e:
        logger.error(f"Error in dossiers list: {e}")
        flash('Error loading dossiers', 'error')
        return render_template('dossiers/list.html', dossiers=[])


@app.route('/dossiers/new', methods=['GET', 'POST'])
def create_dossier():
    """Create new dossier."""
    if request.method == 'GET':
        try:
            frameworks = asyncio.run(api_client.get_hta_frameworks())
            return render_template('dossiers/create.html', frameworks=frameworks)
        except Exception as e:
            logger.error(f"Error loading create form: {e}")
            flash('Error loading form data', 'error')
            return render_template('dossiers/create.html', frameworks={})
    
    elif request.method == 'POST':
        try:
            # Extract form data
            dossier_data = {
                "title": request.form.get('title'),
                "description": request.form.get('description'),
                "hta_framework": request.form.get('hta_framework'),
                "product_profile": {
                    "product_name": request.form.get('product_name'),
                    "active_ingredient": request.form.get('active_ingredient'),
                    "indication": request.form.get('indication'),
                    "therapeutic_area": request.form.get('therapeutic_area', 'other'),
                    "orphan_designation": request.form.get('orphan_designation') == 'on',
                    "breakthrough_therapy": request.form.get('breakthrough_therapy') == 'on'
                },
                "target_price": float(request.form.get('target_price', 0)) if request.form.get('target_price') else None,
                "target_population_size": int(request.form.get('target_population_size', 0)) if request.form.get('target_population_size') else None
            }
            
            # Create dossier via API
            result = asyncio.run(api_client.create_dossier(dossier_data))
            
            if result:
                flash('Dossier created successfully!', 'success')
                return redirect(url_for('dossier_detail', dossier_id=result['id']))
            else:
                flash('Error creating dossier', 'error')
                return redirect(url_for('create_dossier'))
                
        except Exception as e:
            logger.error(f"Error creating dossier: {e}")
            flash('Error creating dossier', 'error')
            return redirect(url_for('create_dossier'))


@app.route('/dossiers/<dossier_id>')
def dossier_detail(dossier_id: str):
    """View dossier details."""
    try:
        dossier = asyncio.run(api_client.get_dossier(dossier_id))
        if not dossier:
            flash('Dossier not found', 'error')
            return redirect(url_for('dossiers_list'))
        
        return render_template('dossiers/detail.html', dossier=dossier)
    except Exception as e:
        logger.error(f"Error loading dossier detail: {e}")
        flash('Error loading dossier', 'error')
        return redirect(url_for('dossiers_list'))


@app.route('/evidence')
def evidence_management():
    """Evidence management page."""
    return render_template('evidence/index.html')


@app.route('/economics')
def economics_dashboard():
    """Health economics dashboard."""
    return render_template('economics/index.html')


@app.route('/hta')
def hta_frameworks():
    """HTA frameworks overview."""
    try:
        frameworks = asyncio.run(api_client.get_hta_frameworks())
        return render_template('hta/frameworks.html', frameworks=frameworks)
    except Exception as e:
        logger.error(f"Error loading HTA frameworks: {e}")
        flash('Error loading HTA frameworks', 'error')
        return render_template('hta/frameworks.html', frameworks={})


@app.route('/api/health')
def health_check():
    """Health check endpoint for the Flask UI."""
    return jsonify({
        'status': 'healthy',
        'service': 'medai-dossier-ui',
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
