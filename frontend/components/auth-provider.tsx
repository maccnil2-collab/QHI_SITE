"use client";
import { createContext, useCallback, useContext, useMemo, useState } from "react";

type User={id:number;email_normalized:string;full_name:string;phone:string|null;preferred_locale:string;role:string;email_verified:boolean};
type AuthResult={access_token:string;customer:User};
type AuthContextValue={user:User|null;token:string|null;busy:boolean;signIn:(email:string,password:string)=>Promise<void>;register:(data:{email:string;password:string;full_name:string;phone:string|null;preferred_locale:string})=>Promise<void>;signOut:()=>Promise<void>;api:<T>(path:string,options?:RequestInit)=>Promise<T>;download:(path:string)=>Promise<Blob>;setUser:(user:User)=>void};
const apiBase=process.env.NEXT_PUBLIC_API_URL??"http://localhost:8000/api/v1";
const Context=createContext<AuthContextValue|null>(null);

export function AuthProvider({children}:{children:React.ReactNode}){
 const [user,setUser]=useState<User|null>(null);const [token,setToken]=useState<string|null>(null);const [busy,setBusy]=useState(false);
 const api=useCallback(async<T,>(path:string,options:RequestInit={}):Promise<T>=>{if(!token)throw new Error("Authentication required");const response=await fetch(`${apiBase}${path}`,{...options,headers:{Authorization:`Bearer ${token}`,"Content-Type":"application/json",...options.headers}});if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(body.detail??`Request failed (${response.status})`)}return response.status===204?undefined as T:response.json() as Promise<T>},[token]);
 const download=useCallback(async(path:string):Promise<Blob>=>{if(!token)throw new Error("Authentication required");const response=await fetch(`${apiBase}${path}`,{headers:{Authorization:`Bearer ${token}`}});if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(body.detail??`Download failed (${response.status})`)}return response.blob()},[token]);
 async function authenticate(path:string,body:object){setBusy(true);try{const response=await fetch(`${apiBase}${path}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});if(!response.ok){const data=await response.json().catch(()=>({}));throw new Error(data.detail??`Request failed (${response.status})`)}const result=await response.json() as AuthResult;setToken(result.access_token);setUser(result.customer)}finally{setBusy(false)}}
 const signIn=(email:string,password:string)=>authenticate("/auth/login",{email,password});
 const register=(data:{email:string;password:string;full_name:string;phone:string|null;preferred_locale:string})=>authenticate("/auth/register",data);
 async function signOut(){try{await api("/auth/logout",{method:"POST"})}finally{setToken(null);setUser(null)}}
 const value=useMemo(()=>({user,token,busy,signIn,register,signOut,api,download,setUser}),[user,token,busy,api,download]);
 return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function useAuth(){const context=useContext(Context);if(!context)throw new Error("AuthProvider is missing");return context}
