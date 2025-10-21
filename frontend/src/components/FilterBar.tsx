import { X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import type { SearchFilters } from "@/lib/api";

interface FilterBarProps {
  filters: SearchFilters;
  onFilterChange: (filters: SearchFilters) => void;
  onClear: () => void;
}

const COMMON_AMENITIES = [
  "WiFi",
  "Kitchen",
  "Air conditioning",
  "Heating",
  "Washer",
  "Elevator",
  "Parking",
  "TV",
];

const FilterBar = ({ filters, onFilterChange, onClear }: FilterBarProps) => {
  const handlePriceChange = (value: number[]) => {
    onFilterChange({ ...filters, price_range: [value[0], value[1]] });
  };

  const handleAmenityToggle = (amenity: string) => {
    const current = filters.amenities || [];
    const updated = current.includes(amenity)
      ? current.filter((a) => a !== amenity)
      : [...current, amenity];
    onFilterChange({ ...filters, amenities: updated });
  };

  return (
    <Card className="sticky top-20 z-40 mb-6 p-4">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-semibold">Filters</h3>
        <Button variant="ghost" size="sm" onClick={onClear}>
          Clear all
        </Button>
      </div>

      {/* Active filters */}
      <div className="mb-4 flex flex-wrap gap-2">
        {filters.location && (
          <Badge variant="secondary" className="gap-1">
            {filters.location}
            <X className="h-3 w-3 cursor-pointer" onClick={() => onFilterChange({ ...filters, location: undefined })} />
          </Badge>
        )}
        {filters.guests && (
          <Badge variant="secondary" className="gap-1">
            {filters.guests} guests
            <X className="h-3 w-3 cursor-pointer" onClick={() => onFilterChange({ ...filters, guests: undefined })} />
          </Badge>
        )}
        {filters.dates && (
          <Badge variant="secondary" className="gap-1">
            {filters.dates.check_in} to {filters.dates.check_out}
            <X className="h-3 w-3 cursor-pointer" onClick={() => onFilterChange({ ...filters, dates: undefined })} />
          </Badge>
        )}
      </div>

      {/* Price range */}
      <div className="mb-4">
        <label className="mb-2 block text-sm font-medium">
          Price per night: €{filters.price_range?.[0] || 0} - €{filters.price_range?.[1] || 300}
        </label>
        <Slider
          value={filters.price_range || [0, 300]}
          onValueChange={handlePriceChange}
          max={300}
          step={10}
          className="w-full"
        />
      </div>

      {/* Amenities */}
      <div>
        <label className="mb-2 block text-sm font-medium">Amenities</label>
        <div className="grid grid-cols-2 gap-3">
          {COMMON_AMENITIES.map((amenity) => (
            <label key={amenity} className="flex items-center gap-2 text-sm">
              <Checkbox
                checked={filters.amenities?.includes(amenity)}
                onCheckedChange={() => handleAmenityToggle(amenity)}
              />
              {amenity}
            </label>
          ))}
        </div>
      </div>
    </Card>
  );
};

export default FilterBar;
