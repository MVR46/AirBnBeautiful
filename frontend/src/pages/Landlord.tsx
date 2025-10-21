import { useEffect, useState } from "react";
import { Loader2, Sparkles, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import {
  getLandlordPrefill,
  detectAmenitiesFromImages,
  getPriceSuggestions,
  type PrefillData,
  type PriceSuggestion,
} from "@/lib/api";

const AMENITY_GROUPS = {
  Essentials: ["WiFi", "Kitchen", "Air conditioning", "Heating"],
  Bathroom: ["Hair dryer", "Shampoo", "Hot water"],
  Bedroom: ["Hangers", "Bed linens", "Extra pillows"],
  Entertainment: ["TV", "Sound system"],
  Family: ["Crib", "High chair", "Baby bath"],
  Convenience: ["Washer", "Dryer", "Iron", "Elevator"],
  Outdoor: ["Balcony", "Garden", "BBQ grill"],
  Parking: ["Free parking", "Paid parking"],
};

const Landlord = () => {
  const [loading, setLoading] = useState(true);
  const [prefillData, setPrefillData] = useState<PrefillData | null>(null);
  const [selectedPhotos, setSelectedPhotos] = useState<string[]>([]);
  const [amenities, setAmenities] = useState<string[]>([]);
  const [autoDetectedAmenities, setAutoDetectedAmenities] = useState<string[]>([]);
  const [detectingAmenities, setDetectingAmenities] = useState(false);
  const [targetPrice, setTargetPrice] = useState("");
  const [priceSuggestion, setPriceSuggestion] = useState<PriceSuggestion | null>(null);
  const [loadingPrice, setLoadingPrice] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const fetchPrefill = async () => {
      try {
        const data = await getLandlordPrefill();
        setPrefillData(data);
        setSelectedPhotos(data.photos.map((p) => p.id));
        setAmenities(data.amenities);
      } catch (error) {
        toast({
          title: "Error loading data",
          description: "Could not load pre-filled listing.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };
    fetchPrefill();
  }, [toast]);

  const handleDetectAmenities = async () => {
    if (selectedPhotos.length === 0) {
      toast({ title: "No photos selected", description: "Select photos first." });
      return;
    }
    setDetectingAmenities(true);
    try {
      const response = await detectAmenitiesFromImages(selectedPhotos);
      setAutoDetectedAmenities(response.detected);
      toast({
        title: "Amenities detected!",
        description: `Found ${response.detected.length} amenities from your photos.`,
      });
    } catch (error) {
      toast({
        title: "Detection failed",
        description: "Could not analyze photos.",
        variant: "destructive",
      });
    } finally {
      setDetectingAmenities(false);
    }
  };

  const handlePriceSuggestions = async () => {
    if (!targetPrice || !prefillData) return;
    setLoadingPrice(true);
    try {
      // Merge manual and auto-detected amenities
      const allAmenities = [...new Set([...amenities, ...autoDetectedAmenities])];
      const suggestions = await getPriceSuggestions(allAmenities, Number(targetPrice), {
        guests: prefillData.guests,
        beds: prefillData.beds,
        neighborhood: prefillData.neighborhood,
      });
      setPriceSuggestion(suggestions);
    } catch (error) {
      toast({
        title: "Error",
        description: "Could not generate price suggestions.",
        variant: "destructive",
      });
    } finally {
      setLoadingPrice(false);
    }
  };

  const handleApplyAmenity = (amenity: string) => {
    const allAmenities = [...amenities, ...autoDetectedAmenities];
    if (!allAmenities.includes(amenity)) {
      setAmenities([...amenities, amenity]);
      toast({ title: "Amenity added", description: `${amenity} added to your listing.` });
    }
  };

  const handleRemoveAutoDetected = (amenity: string) => {
    setAutoDetectedAmenities(autoDetectedAmenities.filter((a) => a !== amenity));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background py-8">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <Skeleton className="mb-4 h-10 w-1/2" />
          <Skeleton className="mb-8 h-6 w-3/4" />
          <Skeleton className="h-96" />
        </div>
      </div>
    );
  }

  if (!prefillData) return null;

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold">List Your Place (Madrid)</h1>
          <p className="text-muted-foreground">
            We pre-filled a listing for you. Adjust details, choose photos, and let AI help with amenities & pricing.
          </p>
        </div>

        {/* Form */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Basics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="title">Title</Label>
                <Input id="title" defaultValue={prefillData.title} />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label htmlFor="type">Property Type</Label>
                  <Select defaultValue={prefillData.type}>
                    <SelectTrigger id="type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Entire apartment">Entire apartment</SelectItem>
                      <SelectItem value="Private room">Private room</SelectItem>
                      <SelectItem value="Shared room">Shared room</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="guests">Guests</Label>
                  <Input id="guests" type="number" defaultValue={prefillData.guests} />
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                <div>
                  <Label htmlFor="beds">Beds</Label>
                  <Input id="beds" type="number" defaultValue={prefillData.beds} />
                </div>
                <div>
                  <Label htmlFor="baths">Baths</Label>
                  <Input id="baths" type="number" defaultValue={prefillData.baths} />
                </div>
                <div>
                  <Label htmlFor="bedrooms">Bedrooms</Label>
                  <Input id="bedrooms" type="number" defaultValue={prefillData.bedrooms} />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Location</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="address">Address</Label>
                <Input id="address" defaultValue={prefillData.address} />
              </div>
              <div>
                <Label htmlFor="neighborhood">Neighborhood</Label>
                <Select defaultValue={prefillData.neighborhood}>
                  <SelectTrigger id="neighborhood">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Centro">Centro</SelectItem>
                    <SelectItem value="Malasaña">Malasaña</SelectItem>
                    <SelectItem value="Chueca">Chueca</SelectItem>
                    <SelectItem value="Lavapiés">Lavapiés</SelectItem>
                    <SelectItem value="Salamanca">Salamanca</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Photos & CV Amenities</CardTitle>
              <CardDescription>Select photos and auto-detect amenities using computer vision</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                {prefillData.all_ready_photos.map((photo) => (
                  <label key={photo.id} className="relative cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedPhotos.includes(photo.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedPhotos([...selectedPhotos, photo.id]);
                        } else {
                          setSelectedPhotos(selectedPhotos.filter((id) => id !== photo.id));
                        }
                      }}
                      className="peer sr-only"
                    />
                    <img
                      src={photo.url}
                      alt=""
                      className="aspect-square w-full rounded-lg object-cover ring-2 ring-transparent transition-all peer-checked:ring-primary"
                    />
                  </label>
                ))}
              </div>
              <Button onClick={handleDetectAmenities} disabled={detectingAmenities || selectedPhotos.length === 0}>
                {detectingAmenities ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Detecting...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Auto-detect amenities from photos
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Amenities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Auto-detected amenities section */}
                {autoDetectedAmenities.length > 0 && (
                  <div className="rounded-lg border bg-muted/30 p-4">
                    <h4 className="mb-3 font-medium text-sm text-muted-foreground">
                      Auto-Detected from Photos
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {autoDetectedAmenities.map((amenity) => (
                        <Badge
                          key={amenity}
                          variant="secondary"
                          className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground"
                          onClick={() => handleRemoveAutoDetected(amenity)}
                        >
                          {amenity}
                          <span className="ml-1 text-xs">×</span>
                        </Badge>
                      ))}
                    </div>
                    <p className="mt-2 text-xs text-muted-foreground">
                      Click to remove an amenity
                    </p>
                  </div>
                )}

                {/* Manual selection checkboxes */}
                {Object.entries(AMENITY_GROUPS).map(([group, items]) => (
                  <div key={group}>
                    <h4 className="mb-3 font-medium">{group}</h4>
                    <div className="grid grid-cols-2 gap-3">
                      {items.map((amenity) => (
                        <label key={amenity} className="flex items-center gap-2 text-sm">
                          <Checkbox
                            checked={amenities.includes(amenity)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setAmenities([...amenities, amenity]);
                              } else {
                                setAmenities(amenities.filter((a) => a !== amenity));
                              }
                            }}
                          />
                          {amenity}
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Price Optimizer
              </CardTitle>
              <CardDescription>Reach your target price with AI-powered recommendations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1">
                  <Label htmlFor="currentPrice">Current Price (€/night)</Label>
                  <Input id="currentPrice" type="number" defaultValue={prefillData.price_per_night} disabled />
                </div>
                <div className="flex-1">
                  <Label htmlFor="targetPrice">Target Price (€/night)</Label>
                  <Input
                    id="targetPrice"
                    type="number"
                    value={targetPrice}
                    onChange={(e) => setTargetPrice(e.target.value)}
                    placeholder="100"
                  />
                </div>
              </div>
              <Button onClick={handlePriceSuggestions} disabled={loadingPrice || !targetPrice}>
                {loadingPrice ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Calculating...
                  </>
                ) : (
                  "Suggest amenities to reach target"
                )}
              </Button>

              {priceSuggestion && (
                <div className="mt-6 space-y-4 rounded-lg border bg-muted/30 p-4">
                  <div>
                    <h4 className="mb-2 font-semibold">Feature Importance</h4>
                    <div className="space-y-2">
                      {priceSuggestion.featureImportance.map((item) => (
                        <div key={item.feature} className="flex items-center gap-2">
                          <span className="w-32 text-sm">{item.feature}</span>
                          <div className="h-2 flex-1 overflow-hidden rounded-full bg-secondary">
                            <div
                              className="h-full bg-primary"
                              style={{ width: `${item.importance * 100}%` }}
                            />
                          </div>
                          <span className="text-sm text-muted-foreground">
                            {(item.importance * 100).toFixed(0)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="mb-2 font-semibold">Recommended Additions</h4>
                    <div className="flex flex-wrap gap-2">
                      {priceSuggestion.recommendedAdditions.map((rec) => (
                        <Badge
                          key={rec.amenity}
                          variant="secondary"
                          className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                          onClick={() => handleApplyAmenity(rec.amenity)}
                        >
                          {rec.amenity} (+€{rec.estimatedLift})
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {priceSuggestion.notes && (
                    <p className="text-xs text-muted-foreground">{priceSuggestion.notes}</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Landlord;
