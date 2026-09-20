"use client";

import { useState } from "react";
import { LogIn, UserPlus, Loader2, ShieldCheck, AlertCircle } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { apiFetch, setAuthToken } from "@/lib/api";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthenticated: (username: string) => void;
}

export function AuthModal({ isOpen, onClose, onAuthenticated }: AuthModalProps) {
  const [activeTab, setActiveTab] = useState<"login" | "register">("login");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form states
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  const [regEmail, setRegEmail] = useState("");
  const [regUsername, setRegUsername] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regFullName, setRegFullName] = useState("");

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    if (!loginUsername.trim() || !loginPassword.trim()) {
      setErrorMessage("Please enter both username and password.");
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const res: any = await apiFetch("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({
          username: loginUsername.trim(),
          password: loginPassword.trim(),
        }),
      });

      if (res?.access_token) {
        setAuthToken(res.access_token);
        onAuthenticated(res.username || loginUsername.trim());
        onClose();
      } else {
        throw new Error("Login failed: Access token missing.");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    if (!regEmail.trim() || !regUsername.trim() || !regPassword.trim()) {
      setErrorMessage("Please fill in all required registration fields.");
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      await apiFetch("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: regEmail.trim(),
          username: regUsername.trim(),
          password: regPassword.trim(),
          full_name: regFullName.trim() || undefined,
        }),
      });

      // Explicitly log in user after successful registration
      const loginRes: any = await apiFetch("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({
          username: regUsername.trim(),
          password: regPassword.trim(),
        }),
      });

      if (loginRes?.access_token) {
        setAuthToken(loginRes.access_token);
        onAuthenticated(loginRes.username || regUsername.trim());
        onClose();
      } else {
        setSuccessMessage("Account created successfully. Please log in.");
        setActiveTab("login");
        setLoginUsername(regUsername.trim());
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[425px] border-slate-800 bg-slate-950 text-white">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold text-sky-400">
            <ShieldCheck className="h-6 w-6 text-sky-400" />
            RitaDrishti Security Portal
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Sign in or register an auditor account to access enterprise risk analytics.
          </DialogDescription>
        </DialogHeader>

        {errorMessage && (
          <div className="flex items-start gap-2 p-3 rounded bg-red-950/60 border border-red-800 text-red-300 text-sm">
            <AlertCircle className="h-5 w-5 shrink-0 text-red-400 mt-0.5" />
            <span>{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="flex items-center gap-2 p-3 rounded bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm">
            <ShieldCheck className="h-5 w-5 shrink-0 text-emerald-400" />
            <span>{successMessage}</span>
          </div>
        )}

        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="w-full mt-2">
          <TabsList className="grid w-full grid-cols-2 bg-slate-900 border border-slate-800">
            <TabsTrigger value="login" className="data-[state=active]:bg-sky-600 data-[state=active]:text-white">
              <LogIn className="h-4 w-4 mr-2" />
              Sign In
            </TabsTrigger>
            <TabsTrigger value="register" className="data-[state=active]:bg-sky-600 data-[state=active]:text-white">
              <UserPlus className="h-4 w-4 mr-2" />
              Register
            </TabsTrigger>
          </TabsList>

          <TabsContent value="login">
            <form onSubmit={handleLogin} className="space-y-4 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Username</label>
                <input
                  type="text"
                  required
                  value={loginUsername}
                  onChange={(e) => setLoginUsername(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none"
                  placeholder="analyst_auditor"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none"
                  placeholder="••••••••••••"
                />
              </div>
              <Button type="submit" disabled={loading} className="w-full bg-sky-600 hover:bg-sky-500 text-white font-semibold">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <LogIn className="h-4 w-4 mr-2" />}
                Sign In to Dashboard
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="register">
            <form onSubmit={handleRegister} className="space-y-3 pt-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none"
                  placeholder="auditor@firm.com"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Username</label>
                <input
                  type="text"
                  required
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none"
                  placeholder="auditor_jane"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none"
                  placeholder="••••••••••••"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Full Name (Optional)</label>
                <input
                  type="text"
                  value={regFullName}
                  onChange={(e) => setRegFullName(e.target.value)}
                  className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none"
                  placeholder="Jane Doe"
                />
              </div>
              <Button type="submit" disabled={loading} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold mt-2">
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <UserPlus className="h-4 w-4 mr-2" />}
                Create Auditor Account
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
