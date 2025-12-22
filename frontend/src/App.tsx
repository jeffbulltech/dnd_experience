import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { useAuth } from "./contexts/AuthContext";
import CampaignSelect from "./pages/CampaignSelect";
import CharacterBuilder from "./pages/CharacterBuilder/CharacterBuilder";
import CharacterCreation from "./pages/CharacterCreation";
import Game from "./pages/Game";
import Login from "./pages/Login";
import Register from "./pages/Register";

function ProtectedLayout(): JSX.Element {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-br from-shadow-black via-arcane-blue-900/20 to-shadow-black">
      <header className="relative border-b-2 border-dragon-gold-600/40 bg-gradient-to-r from-arcane-blue-900/95 via-arcane-blue-800/95 to-arcane-blue-900/95 backdrop-blur-sm">
        <div className="absolute inset-0 bg-parchment-texture opacity-10"></div>
        <div className="relative mx-auto flex max-w-5xl items-center justify-between p-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-dragon-gold-500/60 bg-gradient-to-br from-dragon-gold-400 to-dragon-gold-700 shadow-lg">
              <span className="text-xl font-display text-shadow-black">⚔</span>
            </div>
            <div>
              <h1 className="text-3xl font-display font-bold text-dragon-gold-300 drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]">
                D&D AI Game Master
              </h1>
              {user ? (
                <p className="text-sm font-medium text-parchment-200/90">
                  Adventurer: <span className="text-dragon-gold-200">{user.display_name}</span>
                </p>
              ) : null}
            </div>
          </div>
          <button
            className="fantasy-button text-base"
            onClick={logout}
            type="button"
          >
            Sign Out
          </button>
        </div>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}

function App(): JSX.Element {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-shadow-black via-arcane-blue-900/20 to-shadow-black">
        <div className="text-center">
          <div className="mb-4 text-6xl font-display text-dragon-gold-400 animate-pulse">⚔</div>
          <p className="text-xl font-display text-parchment-200 drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]">
            Gathering party...
          </p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/campaigns" replace /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/campaigns" replace /> : <Register />} />
      <Route element={user ? <ProtectedLayout /> : <Navigate to="/login" replace />}>
        <Route path="/" element={<Navigate to="/campaigns" replace />} />
        <Route path="/campaigns" element={<CampaignSelect />} />
        <Route path="/characters/new" element={<CharacterCreation />} />
        <Route path="/builder" element={<CharacterBuilder />} />
        <Route path="/game/:campaignId" element={<Game />} />
      </Route>
      <Route path="*" element={<Navigate to={user ? "/campaigns" : "/login"} replace />} />
    </Routes>
  );
}

export default App;
