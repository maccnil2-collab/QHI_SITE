"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

type User = { id:number; email_normalized:string; full_name:string; phone:string|null; preferred_locale:string; role:string; email_verified:boolean };
type AuthResult = { customer:User; csrf_token:string };
type AuthContextValue = {
  user:User|null;
  ready:boolean;
  busy:boolean;
  signIn:(email:string,password:string)=>Promise<void>;
  register:(data:{email:string;password:string;full_name:string;phone:string|null;preferred_locale:string})=>Promise<void>;
  signOut:()=>Promise<void>;
  api:<T>(path:string,options?:RequestInit)=>Promise<T>;
  download:(path:string)=>Promise<Blob>;
  setUser:(user:User)=>void;
};

const apiBase=process.env.NEXT_PUBLIC_API_URL??"http://localhost:8000/api/v1";
const Context=createContext<AuthContextValue|null>(null);

function errorDetail(body:unknown,fallback:string):string {
  if(typeof body==="object"&&body!==null&&"detail" in body&&typeof body.detail==="string")return body.detail;
  return fallback;
}

export function AuthProvider({children}:{children:React.ReactNode}){
  const [user,setUser]=useState<User|null>(null);
  const [csrfToken,setCsrfToken]=useState<string|null>(null);
  const [ready,setReady]=useState(false);
  const [busy,setBusy]=useState(false);

  useEffect(()=>{
    let active=true;
    fetch(`${apiBase}/auth/me`,{credentials:"include"})
      .then(async response=>{
        if(!response.ok)return null;
        const csrf=response.headers.get("X-CSRF-Token");
        if(active)setCsrfToken(csrf);
        return await response.json() as User;
      })
      .then(customer=>{if(active)setUser(customer)})
      .catch(()=>{if(active)setUser(null)})
      .finally(()=>{if(active)setReady(true)});
    return ()=>{active=false};
  },[]);

  const api=useCallback(async<T,>(path:string,options:RequestInit={}):Promise<T>=>{
    const headers=new Headers(options.headers);
    const method=(options.method??"GET").toUpperCase();
    if(typeof options.body==="string"&&!headers.has("Content-Type"))headers.set("Content-Type","application/json");
    if(!["GET","HEAD","OPTIONS"].includes(method)){
      if(csrfToken)headers.set("X-CSRF-Token",csrfToken);
    }
    const response=await fetch(`${apiBase}${path}`,{...options,credentials:"include",headers});
    if(!response.ok){const body=await response.json().catch(()=>({}));if(response.status===401){setUser(null);setCsrfToken(null)}throw new Error(errorDetail(body,`Request failed (${response.status})`))}
    return response.status===204?undefined as T:response.json() as Promise<T>;
  },[csrfToken]);

  const download=useCallback(async(path:string):Promise<Blob>=>{
    const response=await fetch(`${apiBase}${path}`,{credentials:"include"});
    if(!response.ok){const body=await response.json().catch(()=>({}));if(response.status===401){setUser(null);setCsrfToken(null)}throw new Error(errorDetail(body,`Download failed (${response.status})`))}
    return response.blob();
  },[]);

  const authenticate=useCallback(async(path:string,body:object)=>{
    setBusy(true);
    try{
      const response=await fetch(`${apiBase}${path}`,{method:"POST",credentials:"include",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
      if(!response.ok){const data=await response.json().catch(()=>({}));throw new Error(errorDetail(data,`Request failed (${response.status})`))}
      const result=await response.json() as AuthResult;
      setCsrfToken(result.csrf_token);
      setUser(result.customer);
    }finally{setBusy(false);setReady(true)}
  },[]);

  const signIn=useCallback((email:string,password:string)=>authenticate("/auth/login",{email,password}),[authenticate]);
  const register=useCallback((data:{email:string;password:string;full_name:string;phone:string|null;preferred_locale:string})=>authenticate("/auth/register",data),[authenticate]);
  const signOut=useCallback(async()=>{try{await api("/auth/logout",{method:"POST"})}finally{setUser(null);setCsrfToken(null)}},[api]);

  const value=useMemo(()=>({user,ready,busy,signIn,register,signOut,api,download,setUser}),[user,ready,busy,signIn,register,signOut,api,download]);
  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function useAuth(){const context=useContext(Context);if(!context)throw new Error("AuthProvider is missing");return context}
