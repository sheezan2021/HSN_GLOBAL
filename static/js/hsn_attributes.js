// Function to load HSN attributes for a given HSN code
async function loadHsnAttributes(hsnCode) {
    try {
        const response = await fetch(`/get_hsn_attributes?hsn_code=${hsnCode}`);
        if (!response.ok) {
            console.log('No attributes found for HSN code:', hsnCode);
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error('Error loading HSN attributes:', error);
        return null;
    }
}

// Function to display variant options in the UI
function displayVariantOptions(attributes) {
    const variantsContainer = document.getElementById('variant-options');
    const optionsContainer = document.getElementById('variant-options-container');
    
    if (!attributes || !attributes.variant_types) {
        variantsContainer.style.display = 'none';
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
