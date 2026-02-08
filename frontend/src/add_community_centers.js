import fs from "fs";
import csv from "csv-parser";
import path from "path";
import { fileURLToPath } from "url";
import {app} from "./firebaseConfig.js"; // Ensure this is the correct relative path
import {
    getDatabase,
    ref,
    push,
    set
} from "firebase/database";

// Fixing the path resolution
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const filePath = path.join(__dirname, "assets", "community_centers.csv");

const db = getDatabase(app);
const communityCentersRef = ref(db, "safe-routes/community-centers");

const uploadCSV = async () => {
    const results = [];
    
    fs.createReadStream(filePath)
        .pipe(csv())
        .on("data", async (row) => {
            try {
                const formattedData = {
                    Co_ordinates: {
                        latitude: parseFloat(row.latitude),
                        longitude: parseFloat(row.longitude),
                    },
                    Type: row.Type,
                };

                const newDocRef = push(communityCentersRef);
                await set(newDocRef, formattedData); // Await the write operation
                
                results.push(formattedData);
            } catch (error) {
                console.error("Error adding data:", error);
            }
        })
        .on("end", () => {
            console.log("Upload complete. Data:");
            console.log(JSON.stringify(results, null, 2));
        });
};

// Run the function
uploadCSV();
