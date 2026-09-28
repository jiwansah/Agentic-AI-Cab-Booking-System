"use client";

import {useState} from "react";
import {ArrowLeft,LockKeyhole,UserPlus,UserRound,UsersRound} from "lucide-react";
import {continueAsGuest,login,register,saveAuthSession} from "@/lib/api";

type Screen="welcome"|"login"|"register"|"guest";
const RIDEPILOT_USER_KEY = "ridepilot_user";

export default function RidePilotApp(){
  const [screen,setScreen]=useState<Screen>("welcome");
  return <main className="min-h-screen bg-slate-50">
    {screen==="welcome"&&<WelcomeScreen onLogin={()=>setScreen("login")} onGuest={()=>setScreen("guest")}/>}
    {screen==="login"&&<LoginScreen onBack={()=>setScreen("welcome")} onRegister={()=>setScreen("register")}/>}
    {screen==="register"&&<RegisterScreen onBack={()=>setScreen("login")}/>}
    {screen==="guest"&&<GuestScreen onBack={()=>setScreen("welcome")}/>}
  </main>;
}

function Brand(){return <div className="flex items-center justify-center gap-2">
  <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-950 text-2xl">🚕</div>
  <span className="text-2xl font-bold tracking-tight text-slate-950">RidePilot</span>
</div>}

function WelcomeScreen({onLogin,onGuest}:{onLogin:()=>void;onGuest:()=>void}){
  return <section className="flex min-h-screen items-center justify-center px-5 py-10"><div className="w-full max-w-md">
    <div className="rounded-[2rem] border border-slate-200 bg-white p-7 shadow-soft sm:p-10">
      <Brand/>
      <div className="mt-10 text-center">
        <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-3xl bg-blue-50 text-4xl">🚕</div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">Your AI Cab Assistant</h1>
        <p className="mt-3 text-sm leading-6 text-slate-500">Tell RidePilot where you want to go and let the AI help you find a ride.</p>
      </div>
      <div className="mt-9 space-y-3">
        <PrimaryButton icon={<LockKeyhole size={18}/>} onClick={onLogin}>Login / Sign Up</PrimaryButton>
        <SecondaryButton icon={<UsersRound size={18}/>} onClick={onGuest}>Continue as Guest</SecondaryButton>
      </div>
      <p className="mt-7 text-center text-xs text-slate-400">Book a ride using AI</p>
    </div>
    <p className="mt-5 text-center text-xs text-slate-400">Responsive • Desktop • Tablet • Mobile</p>
  </div></section>;
}

function LoginScreen({onBack,onRegister}:{onBack:()=>void;onRegister:()=>void}){
  const [identifier,setIdentifier]=useState("");
  const [password,setPassword]=useState("");
  const [error,setError]=useState("");
  const [loading,setLoading]=useState(false);

  async function handleLogin(e:React.FormEvent){
    e.preventDefault(); setError("");
    if(!identifier.trim()){setError("Phone number or login email is required.");return}
    if(!password.trim()){setError("Password is required.");return}
    try{
      setLoading(true);
      const result=await login({identifier:identifier.trim(),password});
      saveAuthSession(result);
      window.location.href = "/chat";
      //alert(`Login successful. User: ${result.user_id}`);
    }catch(err){setError(err instanceof Error?err.message:"Login failed.")}
    finally{setLoading(false)}
  }

  return <section className="flex min-h-screen items-center justify-center px-5 py-8"><div className="w-full max-w-md">
    <BackButton onClick={onBack} label="Back"/>
    <div className="rounded-[2rem] border border-slate-200 bg-white p-7 shadow-soft sm:p-10">
      <Brand/>
      <div className="mt-9">
        <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50"><UserRound className="text-blue-700" size={22}/></div>
        <h1 className="text-2xl font-bold text-slate-950">Welcome back 👋</h1>
        <p className="mt-2 text-sm text-slate-500">Use your registered phone number or email identifier.</p>
      </div>
      <form onSubmit={handleLogin} className="mt-7 space-y-5">
        <Field label="Phone / Email identifier" placeholder="+91 9876543210" value={identifier} onChange={setIdentifier} type="text" autoComplete="username"/>
        <Field label="Password" placeholder="Enter your password" value={password} onChange={setPassword} type="password" autoComplete="current-password"/>
        {error&&<ErrorMessage message={error}/>}
        <PrimaryButton type="submit" disabled={loading}>{loading?"LOGGING IN...":"LOGIN"}</PrimaryButton>
      </form>
      <p className="mt-7 text-center text-sm text-slate-500">Don&apos;t have an account? <button type="button" onClick={onRegister} className="font-semibold text-blue-700 hover:underline">Sign up</button></p>
    </div>
  </div></section>;
}

function RegisterScreen({onBack}:{onBack:()=>void}){
  const [phone,setPhone]=useState("");
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [confirm,setConfirm]=useState("");
  const [error,setError]=useState("");
  const [loading,setLoading]=useState(false);

  async function handleRegister(e:React.FormEvent){
    e.preventDefault();setError("");
    if(!phone.trim() && !email.trim()) { setError("Please provide either a phone number or email address"); return;}
    if(!password){setError("Password is required.");return}
    if(password!==confirm){setError("Passwords do not match.");return}
    try{
      setLoading(true);
      const result=await register({phone:phone.trim(),email:email.trim()||undefined,password});
      saveAuthSession(result);
      window.location.href = "/chat";
      //alert(`Registration successful. User: ${result.user_id}`);
    }catch(err){setError(err instanceof Error?err.message:"Registration failed.")}
    finally{setLoading(false)}
  }

  return <section className="flex min-h-screen items-center justify-center px-5 py-8"><div className="w-full max-w-md">
    <BackButton onClick={onBack} label="Back to login"/>
    <div className="rounded-[2rem] border border-slate-200 bg-white p-7 shadow-soft sm:p-10">
      <Brand/>
      <div className="mt-9">
        <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50"><UserPlus className="text-blue-700" size={22}/></div>
        <h1 className="text-2xl font-bold text-slate-950">Create your account</h1>
        <p className="mt-2 text-sm text-slate-500">Phone number or Email is required.</p>
      </div>
      <form onSubmit={handleRegister} className="mt-7 space-y-5">
        <Field label="Phone number" placeholder="+91 9876543210" value={phone} onChange={setPhone} type="tel" autoComplete="tel"/>
        <Field label="Email" placeholder="you@example.com" value={email} onChange={setEmail} type="email" autoComplete="email"/>
        <Field label="Password" placeholder="Create a password" value={password} onChange={setPassword} type="password" autoComplete="new-password"/>
        <Field label="Confirm password" placeholder="Re-enter your password" value={confirm} onChange={setConfirm} type="password" autoComplete="new-password"/>
        {error&&<ErrorMessage message={error}/>}
        <PrimaryButton type="submit" disabled={loading}>{loading?"CREATING ACCOUNT...":"CREATE ACCOUNT"}</PrimaryButton>
      </form>
    </div>
  </div></section>;
}

function GuestScreen({onBack}:{onBack:()=>void}){
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState("");
  async function handleGuest(){
    setError("");
    try{
      setLoading(true);
      const result=await continueAsGuest();
      saveAuthSession(result);
      window.location.href = "/chat";
      //alert(`Guest session created. Session: ${result.session_id}`);
    }catch(err){setError(err instanceof Error?err.message:"Could not create guest session.")}
    finally{setLoading(false)}
  }
  return <section className="flex min-h-screen items-center justify-center px-5 py-8"><div className="w-full max-w-md">
    <BackButton onClick={onBack} label="Back"/>
    <div className="rounded-[2rem] border border-slate-200 bg-white p-7 text-center shadow-soft sm:p-10">
      <Brand/>
      <div className="mx-auto mt-10 flex h-20 w-20 items-center justify-center rounded-3xl bg-amber-50 text-4xl">👋</div>
      <h1 className="mt-6 text-2xl font-bold text-slate-950">Continue as Guest</h1>
      <p className="mx-auto mt-4 max-w-sm text-sm leading-6 text-slate-500">You can search and book rides without creating an account.</p>
      <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-left text-xs leading-5 text-slate-500">Guest ride history is temporary and should be removed when you sign out according to the backend guest-session policy.</div>
      {error&&<div className="mt-4"><ErrorMessage message={error}/></div>}
      <div className="mt-7"><PrimaryButton onClick={handleGuest} disabled={loading}>{loading?"CREATING GUEST SESSION...":"CONTINUE AS GUEST"}</PrimaryButton></div>
      <button type="button" onClick={onBack} className="mt-6 text-sm font-semibold text-blue-700 hover:underline">Login instead</button>
    </div>
  </div></section>;
}

function BackButton({onClick,label}:{onClick:()=>void;label:string}){
  return <button onClick={onClick} className="mb-5 inline-flex items-center gap-2 rounded-xl px-2 py-2 text-sm font-medium text-slate-600 hover:bg-white"><ArrowLeft size={18}/>{label}</button>
}

function Field({label,placeholder,value,onChange,type,autoComplete}:{label:string;placeholder:string;value:string;onChange:(v:string)=>void;type:string;autoComplete?:string}){
  return <label className="block"><span className="mb-2 block text-sm font-medium text-slate-700">{label}</span><input type={type} autoComplete={autoComplete} value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder} className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-50"/></label>
}

function ErrorMessage({message}:{message:string}){return <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{message}</div>}

function PrimaryButton({children,onClick,type="button",disabled=false,icon}:{children:React.ReactNode;onClick?:()=>void;type?:"button"|"submit";disabled?:boolean;icon?:React.ReactNode}){
  return <button type={type} onClick={onClick} disabled={disabled} className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60">{icon}{children}</button>
}

function SecondaryButton({children,onClick,icon}:{children:React.ReactNode;onClick?:()=>void;icon?:React.ReactNode}){
  return <button type="button" onClick={onClick} className="flex h-12 w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 text-sm font-semibold text-slate-800 transition hover:border-slate-300 hover:bg-slate-50">{icon}{children}</button>
}


