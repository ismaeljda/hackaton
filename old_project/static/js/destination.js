// Destination Page JavaScript - Restaurant focused

class RestaurantManager {
    constructor() {
        this.allRestaurants = [];
        this.filteredRestaurants = [];
        this.filters = {
            cuisine: '',
            price: '',
            rating: ''
        };
        
        this.sortBy = 'rating'; // Default sort by rating
        
        this.init();
    }
    
    init() {
        this.bindFilterEvents();
        this.loadRestaurants();
    }
    
    bindFilterEvents() {
        // Cuisine filter
        const cuisineFilter = document.getElementById('cuisineFilter');
        if (cuisineFilter) {
            cuisineFilter.addEventListener('change', () => {
                this.filters.cuisine = cuisineFilter.value;
                this.loadRestaurants(); // Reload with new filter
            });
        }
        
        // Price filter
        const priceFilter = document.getElementById('priceFilter');
        if (priceFilter) {
            priceFilter.addEventListener('change', () => {
                this.filters.price = priceFilter.value;
                this.loadRestaurants(); // Reload with new filter
            });
        }
        
        // Rating filter
        const ratingFilter = document.getElementById('ratingFilter');
        if (ratingFilter) {
            ratingFilter.addEventListener('change', () => {
                this.filters.rating = parseFloat(ratingFilter.value) || '';
                this.loadRestaurants(); // Reload with new filter
            });
        }
        
        // Sort filter
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', () => {
                this.sortBy = sortSelect.value;
                this.applyFilters();
            });
        }
    }
    
    async loadRestaurants() {
        try {
            this.showLoading(true);
            
            console.log('DEBUG: Loading restaurants for destination:', window.destinationCode);
            
            // Build query parameters for backend filtering
            const params = new URLSearchParams();
            if (this.filters.cuisine) {
                params.append('cuisine_type', this.filters.cuisine);
            }
            if (this.filters.price) {
                params.append('price_level', this.filters.price);
            }
            if (this.filters.rating) {
                params.append('min_rating', this.filters.rating);
            }
            
            const url = `/api/restaurants/${window.destinationCode}?${params.toString()}`;
            console.log('DEBUG: Request URL:', url);
            
            const response = await fetch(url);
            console.log('DEBUG: Response status:', response.status);
            
            const data = await response.json();
            console.log('DEBUG: Response data:', data);
            
            if (data.success) {
                this.allRestaurants = data.restaurants || [];
                console.log('DEBUG: Restaurants loaded:', this.allRestaurants.length);
                this.applyFilters();
            } else {
                console.error('Error loading restaurants:', data.error);
                this.showNoResults();
            }
        } catch (error) {
            console.error('Error loading restaurants:', error);
            this.showNoResults();
        } finally {
            this.showLoading(false);
        }
    }
    
    applyFilters() {
        console.log('DEBUG: Applying filters:', this.filters);
        console.log('DEBUG: Total restaurants before filtering:', this.allRestaurants.length);
        
        this.filteredRestaurants = this.allRestaurants.filter(restaurant => {
            // Cuisine filter
            if (this.filters.cuisine) {
                const restaurantCuisine = restaurant.cuisine_type || '';
                const filterCuisine = this.filters.cuisine.toLowerCase();
                
                // Map filter values to cuisine types
                const cuisineMatches = {
                    'italian': ['italienne', 'pizza', 'italian'],
                    'french': ['française', 'french', 'bistro'],
                    'spanish': ['espagnole', 'spanish', 'tapas'],
                    'asian': ['chinoise', 'japonaise', 'thaïlandaise', 'sushi', 'asian', 'chinese', 'japanese', 'thai'],
                    'mediterranean': ['méditerranéenne', 'mediterranean', 'greek'],
                    'american': ['américaine', 'american', 'burger'],
                    'mexican': ['mexicaine', 'mexican'],
                    'indian': ['indienne', 'indian']
                };
                
                const matchWords = cuisineMatches[filterCuisine] || [filterCuisine];
                const matches = matchWords.some(word => 
                    restaurantCuisine.toLowerCase().includes(word)
                );
                
                if (!matches) {
                    return false;
                }
            }
            
            // Price filter
            if (this.filters.price) {
                const targetPrice = parseInt(this.filters.price);
                const restaurantPrice = restaurant.price_level || 2;
                
                if (restaurantPrice !== targetPrice) {
                    return false;
                }
            }
            
            // Rating filter
            if (this.filters.rating) {
                const minRating = parseFloat(this.filters.rating);
                const restaurantRating = restaurant.rating || 0;
                
                if (restaurantRating < minRating) {
                    return false;
                }
            }
            
            return true;
        });
        
        console.log('DEBUG: Restaurants after filtering:', this.filteredRestaurants.length);
        
        // Apply sorting
        this.sortRestaurants();
        
        this.displayRestaurants();
        this.updateCount();
    }
    
    sortRestaurants() {
        console.log('DEBUG: Sorting by:', this.sortBy);
        
        this.filteredRestaurants.sort((a, b) => {
            switch (this.sortBy) {
                case 'rating':
                    const ratingA = a.rating || 0;
                    const ratingB = b.rating || 0;
                    return ratingB - ratingA; // Highest rating first
                
                case 'reviews':
                    const reviewsA = a.user_ratings_total || 0;
                    const reviewsB = b.user_ratings_total || 0;
                    return reviewsB - reviewsA; // Most reviews first
                
                case 'price_low':
                    const priceLowA = a.price_level || 2;
                    const priceLowB = b.price_level || 2;
                    return priceLowA - priceLowB; // Lowest price first
                
                case 'price_high':
                    const priceHighA = a.price_level || 2;
                    const priceHighB = b.price_level || 2;
                    return priceHighB - priceHighA; // Highest price first
                
                default:
                    return 0;
            }
        });
        
        console.log('DEBUG: Restaurants after sorting:', this.filteredRestaurants.length);
    }
    
    displayRestaurants() {
        const container = document.querySelector('.restaurants-grid');
        const noResults = document.getElementById('noRestaurants');
        
        if (!container) return;
        
        if (this.filteredRestaurants.length === 0) {
            container.innerHTML = '';
            if (noResults) {
                noResults.classList.remove('d-none');
            }
            return;
        }
        
        if (noResults) {
            noResults.classList.add('d-none');
        }
        
        container.innerHTML = this.filteredRestaurants.map(restaurant => 
            this.createRestaurantCard(restaurant)
        ).join('');
    }
    
    createRestaurantCard(restaurant) {
        const priceSymbols = '€'.repeat(restaurant.price_level || 2);
        const rating = restaurant.rating && restaurant.rating > 0 ? restaurant.rating.toFixed(1) : 'N/A';
        const reviewCount = restaurant.user_ratings_total || 0;
        const hasValidRating = restaurant.rating && restaurant.rating > 0;
        
        // Format review count
        const formatReviewCount = (count) => {
            if (count > 1000) return `${(count / 1000).toFixed(1)}k`;
            return count.toString();
        };
        
        return `
            <div class="restaurant-card" data-rating="${restaurant.rating || 0}" data-price="${restaurant.price_level || 2}">
                ${restaurant.photo ? `
                <div class="restaurant-image">
                    <img src="${restaurant.photo}" alt="${restaurant.name}" loading="lazy">
                    <div class="image-overlay">
                        ${hasValidRating ? `
                        <div class="restaurant-rating-overlay">
                            <i class="bi bi-star-fill"></i>
                            <span>${rating}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                ` : ''}
                <div class="restaurant-content">
                    <div class="restaurant-header">
                        <h5 class="restaurant-name">${restaurant.name || 'Restaurant'}</h5>
                        <div class="restaurant-meta">
                            ${!restaurant.photo && hasValidRating ? `
                            <div class="restaurant-rating">
                                <i class="bi bi-star-fill"></i>
                                <span>${rating}</span>
                                ${reviewCount > 0 ? `<small>(${formatReviewCount(reviewCount)})</small>` : ''}
                            </div>
                            ` : ''}
                            <div class="restaurant-price">${priceSymbols}</div>
                        </div>
                    </div>
                    
                    ${restaurant.cuisine_type ? `
                    <div class="restaurant-cuisine">
                        <i class="bi bi-tag"></i>
                        <span>${restaurant.cuisine_type}</span>
                    </div>
                    ` : ''}
                    
                    ${restaurant.address ? `
                    <div class="restaurant-address">
                        <i class="bi bi-geo-alt"></i>
                        <span>${restaurant.address}</span>
                    </div>
                    ` : ''}
                    
                    <div class="restaurant-actions">
                        ${restaurant.website ? `
                        <a href="${restaurant.website}" target="_blank" class="btn btn-outline-primary btn-sm">
                            <i class="bi bi-globe2"></i> Site web
                        </a>
                        ` : ''}
                        ${restaurant.phone ? `
                        <a href="tel:${restaurant.phone}" class="btn btn-outline-success btn-sm">
                            <i class="bi bi-telephone"></i> Appeler
                        </a>
                        ` : ''}
                        ${!restaurant.website && !restaurant.phone ? `
                        <div class="text-muted small">
                            <i class="bi bi-info-circle"></i> Informations limitées
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    updateCount() {
        const countElement = document.getElementById('restaurantsCount');
        if (countElement) {
            countElement.textContent = this.filteredRestaurants.length;
        }
    }
    
    showLoading(show) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = show ? 'flex' : 'none';
        }
    }
    
    showNoResults() {
        const container = document.querySelector('.restaurants-grid');
        const noResults = document.getElementById('noRestaurants');
        
        if (container) {
            container.innerHTML = '';
        }
        if (noResults) {
            noResults.classList.remove('d-none');
        }
        this.updateCount();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Make sure we have the destination code
    if (window.destinationCode) {
        new RestaurantManager();
    } else {
        console.error('Destination code not found');
    }
});