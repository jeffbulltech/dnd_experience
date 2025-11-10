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
    <div className="flex min-h-screen flex-col bg-parchment/60">
      <header className="border-b border-arcane-blue/40 bg-white/85">
        <div className="mx-auto flex max-w-5xl items-center justify-between p-4">
          <div>
            <h1 className="text-xl font-serif text-arcane-blue">D&D AI Game Master</h1>
            {user ? <p className="text-xs text-gray-600">Logged in as {user.display_name}</p> : null}
          </div>
          <button
            className="rounded border border-arcane-blue px-3 py-1 text-sm text-arcane-blue hover:bg-arcane-blue hover:text-white"
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
      <div className="flex min-h-screen items-center justify-center bg-parchment/80 text-arcane-blue">
        Gathering party...
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
