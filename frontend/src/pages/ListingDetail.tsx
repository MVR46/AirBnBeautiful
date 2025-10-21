import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Star, Users, Bed, Bath, MapPin, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import ChatInput from "@/components/ChatInput";
import { useToast } from "@/hooks/use-toast";
import { getListingById, chatWithNeighborhood, type Listing } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const ListingDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [listing, setListing] = useState<Listing | null>(null);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const fetchListing = async () => {
      if (!id) return;
      try {
        const data = await getListingById(id);
        setListing(data);
      } catch (error) {
        toast({
          title: "Error loading listing",
          description: "Could not find this property.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };
    fetchListing();
  }, [id, toast]);

  const handleChatSubmit = async (message: string) => {
    if (!id) return;
    
    const userMessage: Message = { role: "user", content: message };
    setMessages((prev) => [...prev, userMessage]);
    setChatLoading(true);

    try {
      const response = await chatWithNeighborhood(id, message);
      const assistantMessage: Message = { role: "assistant", content: response.reply };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      toast({
        title: "Chat error",
        description: "Could not get a response. Try again.",
        variant: "destructive",
      });
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <Skeleton className="mb-6 h-8 w-32" />
          <div className="grid gap-6 lg:grid-cols-[1fr_400px]">
            <div className="space-y-6">
              <Skeleton className="aspect-[16/9] w-full" />
              <Skeleton className="h-8 w-3/4" />
              <Skeleton className="h-32 w-full" />
            </div>
            <Skeleton className="h-96" />
          </div>
        </div>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h2 className="mb-4 text-2xl font-bold">Listing not found</h2>
          <Link to="/">
            <Button>Back to search</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Back button */}
        <Link to="/" className="mb-6 inline-flex items-center gap-2 text-sm hover:text-primary">
          <ArrowLeft className="h-4 w-4" />
          Back to results
        </Link>

        <div className="grid gap-6 lg:grid-cols-[1fr_400px]">
          {/* Main content */}
          <div className="space-y-6">
            {/* Image gallery */}
            <div className="overflow-hidden rounded-xl">
              <img
                src={listing.thumbnail}
                alt={listing.title}
                className="aspect-[16/9] w-full object-cover"
              />
            </div>

            {/* Title & Details */}
            <div>
              <div className="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>{listing.neighborhood}, Madrid</span>
              </div>
              <h1 className="mb-4 text-3xl font-bold">{listing.title}</h1>
              
              <div className="mb-4 flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-1">
                  <Star className="h-5 w-5 fill-primary text-primary" />
                  <span className="font-semibold">{listing.rating}</span>
                  <span className="text-muted-foreground">({listing.reviews_count} reviews)</span>
                </div>
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Users className="h-5 w-5" />
                  {listing.guests} guests
                </div>
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Bed className="h-5 w-5" />
                  {listing.beds} beds
                </div>
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Bath className="h-5 w-5" />
                  {listing.baths} baths
                </div>
              </div>

              <div className="text-2xl font-bold">
                €{listing.price_per_night} <span className="text-base font-normal text-muted-foreground">/ night</span>
              </div>
            </div>

            {/* Amenities */}
            <Card>
              <CardHeader>
                <CardTitle>Amenities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {listing.amenities.map((amenity) => (
                    <Badge key={amenity} variant="secondary">
                      {amenity}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Map placeholder */}
            <Card>
              <CardHeader>
                <CardTitle>Location</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex h-64 items-center justify-center rounded-lg bg-muted">
                  <MapPin className="h-12 w-12 text-muted-foreground" />
                </div>
                <p className="mt-2 text-sm text-muted-foreground">
                  {listing.neighborhood}, Madrid
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Neighborhood Chat Sidebar */}
          <aside className="lg:sticky lg:top-24 lg:self-start">
            <Card className="h-[600px] overflow-hidden">
              <CardHeader className="border-b">
                <CardTitle>Ask about the neighborhood</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Get insights about safety, noise, cafés, and more
                </p>
              </CardHeader>
              <CardContent className="flex h-[calc(600px-140px)] flex-col p-0">
                {/* Messages */}
                <div className="flex-1 space-y-4 overflow-y-auto p-4">
                  {messages.length === 0 ? (
                    <div className="flex h-full items-center justify-center text-center text-sm text-muted-foreground">
                      Ask anything about {listing.neighborhood}
                    </div>
                  ) : (
                    messages.map((msg, i) => (
                      <div
                        key={i}
                        className={msg.role === "user" ? "flex justify-end" : "flex justify-start"}
                      >
                        <div
                          className={
                            msg.role === "user"
                              ? "max-w-[80%] rounded-lg bg-primary px-4 py-2 text-primary-foreground"
                              : "max-w-[80%] rounded-lg bg-muted px-4 py-2"
                          }
                        >
                          <p className="text-sm">{msg.content}</p>
                        </div>
                      </div>
                    ))
                  )}
                  {chatLoading && (
                    <div className="flex justify-start">
                      <div className="flex items-center gap-2 rounded-lg bg-muted px-4 py-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm">Thinking...</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input */}
                <div className="border-t p-4">
                  <ChatInput
                    onSubmit={handleChatSubmit}
                    placeholder="Is it safe at night?"
                    disabled={chatLoading}
                  />
                </div>
              </CardContent>
            </Card>
          </aside>
        </div>
      </div>
    </div>
  );
};

export default ListingDetail;
