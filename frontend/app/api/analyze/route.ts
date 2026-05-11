import { NextResponse } from "next/server";
import { exec } from "child_process";
import fs from "fs/promises";
import path from "path";

export async function POST(req: Request) {
  const formData = await req.formData();
  const file = formData.get("audio") as File;
  
  if (!file) return NextResponse.json({ error: "No file" }, { status: 400 });

  // 1. Save file temporarily
  const buffer = Buffer.from(await file.arrayBuffer());
  const tempPath = path.join("/tmp", file.name);
  await fs.writeFile(tempPath, buffer);

  // 2. Execute Python Script
  // This runs the model you trained!
  return new Promise((resolve) => {
    exec(`python3 python_backend/predict.py --input "${tempPath}"`, (error, stdout, stderr) => {
      if (error) {
        console.error("Python Error:", stderr);
        resolve(NextResponse.json({ error: "Model Failed" }, { status: 500 }));
      } else {
        // 3. Parse Python Output (JSON) and return to Frontend
        const result = JSON.parse(stdout);
        resolve(NextResponse.json(result));
      }
    });
  });
}