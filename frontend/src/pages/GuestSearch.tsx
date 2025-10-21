import { useState, useEffect } from "react";
import { Loader2, SearchX, X } from "lucide-react";
import ChatInput from "@/components/ChatInput";
import ListingCard from "@/components/ListingCard";
import FilterBar from "@/components/FilterBar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { searchListings, getFeaturedListings, type SearchFilters, type Listing } from "@/lib/api";

const GuestSearch = () => {
  const [loading, setLoading] = useState(false);
  const [listings, setListings] = useState<Listing[]>([]);
  const [featuredListings, setFeaturedListings] = useState<Listing[]>([]);
  const [loadingFeatured, setLoadingFeatured] = useState(true);
  const [filters, setFilters] = useState<SearchFilters>({});
  const [hasSearched, setHasSearched] = useState(false);
  const { toast } = useToast();

  // Load featured listings on mount
  useEffect(() => {
    const loadFeatured = async () => {
      try {
        const response = await getFeaturedListings();
        setFeaturedListings(response.listings);
      } catch (error) {
        console.error("Failed to load featured listings:", error);
      } finally {
        setLoadingFeatured(false);
      }
    };
    loadFeatured();
  }, []);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setHasSearched(true);
    try {
      const response = await searchListings(query);
      setFilters(response.parsed_filters);
      setListings(response.listings);
    } catch (error) {
      toast({
        title: "Search failed",
        description: "Could not connect to the server. Please try again.",
        variant: "destructive",
      });
      setListings([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters: SearchFilters) => {
    setFilters(newFilters);
    // In a real app, trigger a new search with filters
  };

  const handleClearFilters = () => {
    setFilters({});
    setListings([]);
    setHasSearched(false);
  };

  // Helper to render active filter badges
  const renderFilterBadges = () => {
    const badges = [];
    if (filters.guests) badges.push({ key: 'guests', label: `${filters.guests} guests` });
    if (filters.price_range) badges.push({ key: 'price', label: `€${filters.price_range[0]}-€${filters.price_range[1]}` });
    if (filters.location) badges.push({ key: 'location', label: filters.location });
    if (filters.amenities?.length) {
      filters.amenities.forEach((amenity, i) => 
        badges.push({ key: `amenity-${i}`, label: amenity })
      );
    }
    return badges;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Search Section */}
      <section className="border-b bg-gradient-to-b from-muted/30 to-background py-12">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <h1 className="mb-2 text-center text-4xl font-bold tracking-tight">
            Find your perfect stay in Madrid
          </h1>
          <p className="mb-8 text-center text-muted-foreground">
            Tell us what you're looking for and we'll find the best matches
          </p>
          <ChatInput
            onSubmit={handleSearch}
            placeholder="e.g., 2 guests, 3 nights in Chueca next weekend, budget €120/night, close to metro"
            disabled={loading}
            className="mx-auto max-w-2xl"
          />
          <p className="mt-3 text-center text-xs text-muted-foreground">
            Try: "Studio apartment in Malasaña, WiFi and kitchen, under €100/night"
          </p>
        </div>
      </section>

      {/* Results Section */}
      {hasSearched && (
        <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
            {/* Filters Sidebar */}
            <aside className="hidden lg:block">
              <FilterBar
                filters={filters}
                onFilterChange={handleFilterChange}
                onClear={handleClearFilters}
              />
            </aside>

            {/* Results Grid */}
            <div>
              {/* Active Filters */}
              {renderFilterBadges().length > 0 && (
                <div className="mb-4 flex flex-wrap gap-2">
                  <span className="text-sm text-muted-foreground">Filters:</span>
                  {renderFilterBadges().map((badge) => (
                    <Badge key={badge.key} variant="secondary">
                      {badge.label}
                    </Badge>
                  ))}
                </div>
              )}

              {loading ? (
                <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="space-y-3">
                      <Skeleton className="aspect-[4/3] w-full" />
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-4 w-1/2" />
                    </div>
                  ))}
                </div>
              ) : listings.length > 0 ? (
                <>
                  <p className="mb-4 text-sm text-muted-foreground">
                    {listings.length} properties found
                  </p>
                  <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
                    {listings.map((listing) => (
                      <ListingCard key={listing.id} listing={listing} />
                    ))}
                  </div>
                </>
              ) : (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <SearchX className="mb-4 h-16 w-16 text-muted-foreground" />
                  <h3 className="mb-2 text-lg font-semibold">No listings found</h3>
                  <p className="mb-6 text-sm text-muted-foreground">
                    Try adjusting your filters or search query
                  </p>
                  <Button onClick={handleClearFilters}>Start over</Button>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Featured Properties Section */}
      {!hasSearched && (
        <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
          <h2 className="mb-6 text-2xl font-bold">Featured Properties</h2>
          {loadingFeatured ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="space-y-3">
                  <Skeleton className="aspect-[4/3] w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {featuredListings.map((listing) => (
                <ListingCard key={listing.id} listing={listing} />
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
};

export default GuestSearch;
