"use client";
import React, { useState, useEffect } from "react";
import axios from "axios";
import Layout from "../Layouts/Layout";
import { useRouter } from "next/navigation";

const ChangePasswordForm = () => {
  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");
  const [username, setUsername] = useState(""); // State for storing username
  const [email, setEmail] = useState(""); // State for storing email
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/");
    }
  }, [router]);

  useEffect(() => {
    const fetchUserData = async () => {
      const token = localStorage.getItem("access_token"); //Their may be a better way to handle storing tokens
      try {
        const response = await axios.get(
          `${process.env.NEXT_PUBLIC_API_URL}/api/auth/user/`,
          {
            headers: {
              Authorization: `Token ${token}`,
            },
          }
        );
        setUsername(response.data.username);
        setEmail(response.data.email);
      } catch (error) {
        console.error("Error fetching user data:", error);
        // Handle error (e.g., redirect to login page if unauthorized) Im trying to figure out a simple way to do the token refreshing since I make them expire each hour
      }
    };

    fetchUserData();
  }, []); // The empty array ensures this effect runs only once after the initial render

  const handlePasswordChange = async (e) => {
    e.preventDefault();

    if (newPassword !== confirmNewPassword) {
      alert("New passwords do not match.");
      return;
    }

    // Retrieve the token within this function
    const token = localStorage.getItem("access_token");
    if (!token) {
      console.error("No token found");
      alert("You are not logged in. Please log in and try again.");
      return; // Exit the function if no token is found
    }

    const headers = {
      Authorization: `Token ${token}`, // Use the token directly from localStorage
    };

    const payload = {
      new_password1: newPassword,
      new_password2: confirmNewPassword,
    };

    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/password/change/`,
        payload,
        { headers }
      );
      console.log("Password changed successfully", response.data);
      alert("Password changed successfully");
      // Optional: Redirect the user or force a logout here When you guys edit frontend plz add this
    } catch (error) {
      console.error("Error changing password:", error.response?.data || error);
      alert("Error changing password");
    }
  };

  return (
    <Layout>
      <text className="ml-5 text-3xl text-slate-800 font-semibold">
        {" "}
        Change Password{" "}
      </text>
      <div className="ml-12 w-32 border-4 border-blue-400 rounded-full my-2"></div>
      <div className="flex w-full flex-col items-center justify-start min-h-screen bg-white-A700 pt-5 md:pt-2">
        <div className="flex w-[80%] max-w-[600px] flex-col items-center gap-[10px] self-center rounded-[20px] shadow-lg rounded-lg bg-white-A700 p-[30px] ">
          <div className="p-[20px] m-5 w-full">
            <form onSubmit={handlePasswordChange}>
              <div className="mb-4">
                <label
                  htmlFor="newpassword"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  New Password
                </label>
                <input
                  onChange={(e) => setNewPassword(e.target.value)}
                  type="password"
                  id="newpassword"
                  placeholder="New Password"
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div className="mb-4">
                <label
                  htmlFor="confirmpassword"
                  className="block text-gray-700 text-sm font-bold mb-2"
                >
                  Confirm New Password
                </label>
                <input
                  onChange={(e) => setConfirmNewPassword(e.target.value)}
                  type="password"
                  id="confirmpassword"
                  placeholder="Confirm New Password"
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Save Changes
              </button>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ChangePasswordForm;
