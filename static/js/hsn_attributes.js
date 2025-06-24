// Function to load HSN attributes for a given HSN code
async function loadHsnAttributes(hsnCode) {
    try {
        // Clean and format the HSN code
        const cleanHsnCode = String(hsnCode).trim().replace(/[^0-9]/g, '');
        if (!cleanHsnCode) {
            console.log('Invalid HSN code:', hsnCode);
            return null;
        }
        
        const countrySelect = document.getElementById('country');
        const countryCode = countrySelect ? countrySelect.value : 'IN';
        
        console.log('Fetching HSN attributes for:', {
            hsnCode: hsnCode,
            cleanHsnCode: cleanHsnCode,
            countryCode: countryCode
        });
        
        const url = `/get_hsn_attributes?hsn_code=${encodeURIComponent(cleanHsnCode)}&country=${encodeURIComponent(countryCode)}`;
        console.log('Request URL:', url);
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response from server:', response.status, errorText);
            return null;
        }
        
        const data = await response.json();
        console.log('Received HSN attributes:', data);
        return data;
        
    } catch (error) {
        console.error('Error loading HSN attributes:', error);
        return null;
    }
}

// Function to display variant options in the UI
function displayVariantOptions(attributes) {
    console.log('displayVariantOptions called with:', attributes);
    const variantsContainer = document.getElementById('variant-options');
    const optionsContainer = document.getElementById('variant-options-container');
    
    // Always show the container but with appropriate message if no attributes
    variantsContainer.style.display = 'block';
    
    if (!attributes) {
        console.log('No attributes object received');
        optionsContainer.innerHTML = `
            <div class="alert alert-warning p-2 mb-0">
                <i class="fas fa-exclamation-triangle me-1"></i>
                No attributes data received from server.
            </div>`;
        return;
    }
    
    if (!attributes.variant_types) {
        console.log('No variant_types in attributes:', attributes);
        optionsContainer.innerHTML = `
            <div class="alert alert-warning p-2 mb-0">
                <i class="fas fa-exclamation-triangle me-1"></i>
                No variant types found for this HSN code. Attributes received: ${JSON.stringify(attributes)}
            </div>`;
        return;
    }

    let html = '';
    
    // Create form groups for each variant type
    for (const [variantType, options] of Object.entries(attributes.variant_types)) {
        const variantId = `variant-${variantType}`;
        const label = variantType.charAt(0).toUpperCase() + variantType.slice(1);
        
        html += `
        <div class="mb-1">
            <label for="${variantId}" class="form-label small text-muted mb-0">${label}:</label>
            <select class="form-select form-select-sm variant-select" id="${variantId}">
                <option value="">Select ${label}</option>`;
                
        options.forEach(option => {
            html += `<option value="${option}">${option}</option>`;
        });
        
        html += `
            </select>
        </div>`;
    }
    
    optionsContainer.innerHTML = html;
    variantsContainer.style.display = 'block';
    
    // Log the attributes being displayed
    console.log('Displaying variant options:', attributes.variant_types);
    
    // Clear previous selection
    document.getElementById('selected-variant').textContent = 'No variants selected';
}

// Function to get selected variants
function getSelectedVariants() {
    const selects = document.querySelectorAll('.variant-select');
    const variants = {};
    
    selects.forEach(select => {
        if (select.value) {
            const variantType = select.id.replace('variant-', '');
            variants[variantType] = select.value;
        }
    });
    
    return Object.keys(variants).length > 0 ? variants : null;
}

// Function to update the selected variant display
function updateSelectedVariantDisplay() {
    const variants = getSelectedVariants();
    const variantDisplay = document.getElementById('selected-variant');
    
    if (!variants) {
        variantDisplay.textContent = 'No variants selected';
        return;
    }
    
    const variantText = Object.entries(variants)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');
        
    variantDisplay.textContent = `Selected: ${variantText}`;
}

// Add event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Listen for changes in variant selects
    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('variant-select')) {
            updateSelectedVariantDisplay();
        }
    });
});
