import { Outlet } from "react-router-dom";
import Navigation from "../components/Navigation";
import Footer from "../components/Footer";

export default function Layout() {
    return (
        <div className="min-h-[100vh] flex flex-col bg-page-bg text-white font-sans selection:bg-gold/30 selection:text-white relative">
            <Navigation />
            <main className="flex-1 flex flex-col w-full relative">
                <Outlet />
            </main>
            <Footer />
        </div>
    );
}
