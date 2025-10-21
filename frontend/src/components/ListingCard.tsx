import { Star, Users, Bed, Bath } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import type { Listing } from "@/lib/api";

interface ListingCardProps {
  listing: Listing;
}

const ListingCard = ({ listing }: ListingCardProps) => {
  return (
    <Link to={`/listing/${listing.id}`}>
      <Card className="group overflow-hidden transition-all hover:shadow-lg">
        <div className="relative aspect-[4/3] overflow-hidden">
          <img
            src={listing.thumbnail}
            alt={listing.title}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
          <Badge className="absolute right-2 top-2 bg-card/90 text-foreground">
            {listing.neighborhood}
          </Badge>
        </div>
        <CardContent className="p-4">
          <div className="mb-2 flex items-start justify-between gap-2">
            <h3 className="line-clamp-2 font-semibold">{listing.title}</h3>
            <div className="flex shrink-0 items-center gap-1 text-sm">
              <Star className="h-4 w-4 fill-primary text-primary" />
              <span className="font-medium">{listing.rating}</span>
              <span className="text-muted-foreground">({listing.reviews_count})</span>
            </div>
          </div>
          
          <div className="mb-3 flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Users className="h-4 w-4" />
              {listing.guests}
            </div>
            <div className="flex items-center gap-1">
              <Bed className="h-4 w-4" />
              {listing.beds}
            </div>
            <div className="flex items-center gap-1">
              <Bath className="h-4 w-4" />
              {listing.baths}
            </div>
          </div>

          <div className="mb-3 flex flex-wrap gap-1">
            {listing.amenities.slice(0, 3).map((amenity) => (
              <Badge key={amenity} variant="secondary" className="text-xs">
                {amenity}
              </Badge>
            ))}
            {listing.amenities.length > 3 && (
              <Badge variant="secondary" className="text-xs">
                +{listing.amenities.length - 3}
              </Badge>
            )}
          </div>

          <div className="flex items-baseline gap-1">
            <span className="text-lg font-bold">€{listing.price_per_night}</span>
            <span className="text-sm text-muted-foreground">/ night</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};

export default ListingCard;
