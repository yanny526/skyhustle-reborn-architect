
import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/components/ui/use-toast";

const Index = () => {
  const { toast } = useToast();

  const handlePlayClick = () => {
    toast({
      title: "Game Information",
      description: "SkyHustle is a Telegram strategy RPG. To play, search for the bot on Telegram.",
      duration: 5000,
    });
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-sky-900 to-indigo-900">
      <div className="container max-w-4xl px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-4">SkyHustle</h1>
          <p className="text-xl text-sky-100">Aerial Strategy RPG for Telegram</p>
        </div>

        <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white mb-6">
          <CardHeader>
            <CardTitle className="text-2xl">Build Your Aerial Empire</CardTitle>
            <CardDescription className="text-sky-200">Command the skies, mine resources, research technologies, and dominate your opponents</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-xl font-semibold mb-2">🏗️ Base Building</h3>
                <p className="text-sky-100">Construct and upgrade various buildings to improve your aerial base's capabilities</p>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">⛏️ Resource Mining</h3>
                <p className="text-sky-100">Gather metal, crystal, and fuel to fuel your expansion and military might</p>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">🔬 Tech Research</h3>
                <p className="text-sky-100">Unlock powerful technologies that give you an edge in battle and production</p>
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">⚔️ Military Combat</h3>
                <p className="text-sky-100">Train various units and engage in strategic battles with other players</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/10 backdrop-blur-md border-white/20 text-white mb-6">
          <CardHeader>
            <CardTitle className="text-2xl">Game Features</CardTitle>
            <CardDescription className="text-sky-200">SkyHustle runs entirely through Telegram with persistent state</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white/5 p-4 rounded-lg">
                <h3 className="font-medium mb-2">🏭 Base Management</h3>
                <ul className="list-disc pl-5 text-sm text-sky-100">
                  <li>Command Center</li>
                  <li>Resource Mines</li>
                  <li>Military Facilities</li>
                  <li>Storage Buildings</li>
                </ul>
              </div>
              <div className="bg-white/5 p-4 rounded-lg">
                <h3 className="font-medium mb-2">👨‍🔬 Technology Tree</h3>
                <ul className="list-disc pl-5 text-sm text-sky-100">
                  <li>Mining Efficiency</li>
                  <li>Ship Weapons</li>
                  <li>Ship Armor</li>
                  <li>Defense Systems</li>
                </ul>
              </div>
              <div className="bg-white/5 p-4 rounded-lg">
                <h3 className="font-medium mb-2">🚀 Military Units</h3>
                <ul className="list-disc pl-5 text-sm text-sky-100">
                  <li>Fighters</li>
                  <li>Bombers</li>
                  <li>Cruisers</li>
                  <li>Spy Drones</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        <Separator className="my-6 bg-white/20" />
        
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Ready to Command the Skies?</h2>
          <p className="text-sky-100 mb-6">Join SkyHustle now and build your aerial empire!</p>
          <Button 
            className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-8 py-6 rounded-lg hover:from-blue-600 hover:to-indigo-700 transition-all shadow-lg"
            onClick={handlePlayClick}
          >
            Play SkyHustle
          </Button>
        </div>

        <div className="text-center mt-12 text-sm text-sky-300">
          <p>© 2025 SkyHustle - A Telegram Strategy RPG</p>
          <p className="mt-1">Built with Python, python-telegram-bot, and Google Sheets</p>
        </div>
      </div>
    </div>
  );
};

export default Index;
