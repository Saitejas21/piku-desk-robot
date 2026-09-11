PIKU THE SLEEPY BUNNY

Start with Piku-build-guide.docx for the shopping links and four-page build.
Piku-preview.png shows the actual CAD. Piku-face-expressions.png shows all
nine exact 128 x 64 OLED frames, enlarged so you can see the details.

PRINT THESE TWO FILES
cad/piku_body.stl
cad/piku_back.stl

Print one each in PLA, 100 percent scale in millimetres, 0.2 mm layers,
3 walls, 15 percent infill, 0.4 mm nozzle. Both files lie on the print bed.
Body: face down, open side up. Back: exterior down, locating lip up.
No supports expected in these orientations. The flat surfaces between the
small rounded front edges provide the initial bed contact.
Finished size: about 55 mm wide x 34 mm deep x 64 mm tall, including paws/ears.
Two M2 x 6 mm self-tapping screws close the back. Tighten gently.
Use the matching new body and lid together; the old lid is a different shape.

UPLOAD THIS SKETCH
firmware/Piku/Piku.ino
Keep piku_faces.h in the same folder; it holds all the full-face bitmaps.
Arduino board: ESP32C3 Dev Module. USB CDC On Boot: Enabled. Flash: 4 MB.
Install Adafruit SSD1306 and Adafruit GFX Library and their dependencies.
OLED wiring: 3V3, GND, SDA to GPIO4, SCL to GPIO5.
TTP223: use the small RED 15 x 11 mm board, not the larger blue board.
Wiring: 3V3, GND, output to GPIO3. Active-high momentary mode.
The two boards share 3V3 and ground through insulated Y leads.

PIKU'S PERSONALITY
A sleepy bunny with one tilted ear, small arms, tiny toes and a curious face.
Every OLED expression includes a face outline, eyes, nose, mouth and cheeks.
The single-color OLED draws all marks in its pixel color; cheeks are not pink.
Idle: blink and glance left/right. Touch: smile. Double-tap within 450 ms:
heart eyes. Hold for two seconds: shy wink. Sleep after 60 seconds idle.
Touch to wake with a surprised face, then a smile. Leave the crown alone for
two seconds at startup while the touch sensor settles.
The robot body stays still. There are no motors, microphone or battery.

EDITABLE CAD
STEP and build123d Python source are in cad/ for later changes.
piku_assembly.step shows the assembled shell with the real idle-face artwork.
piku_face_pixels.json is the bitmap input used by the assembly generator.
Do not print the assembly: its screen and pixels are preview shapes only.
The screen artwork is shown at the OLED's nominal 21.74 x 10.87 mm active area.
The viewing aperture is 25 x 16 mm. Align the lit display by hand before taping.
STL is unitless; select millimetres. Do not scale the shell to fit a board.
Local interactive CAD viewer links are in cad/preview-links.md.

CHECKS AND LIMITS
Both print parts are valid single CAD solids with positive volume.
STL checks found zero open/nonmanifold edges and consistent triangle winding.
The body and lid have zero positive-volume overlap in the CAD assembly.
Lid clearance is 0.3 mm per side. Main walls are 2 mm; front is 3 mm.
Crown sensing patch is 0.8 mm at centre and about 0.68 mm at its curved edges.
The small red touch board fits the nominal 18 x 16 mm recess footprint.
Received module dimensions, tape mounting and touch sensitivity need a real
fit test. Enclosure has not been physically printed or assembled here.
Firmware is source-reviewed; it has not been compiled or hardware-tested here.
The guide was rendered with Word and every page visually reviewed.

Cream or pastel PLA suits Piku. Paint the inner ear recesses if you like.
Keep the thin crown touch patch unpainted and use insulating tape under boards.

Original Piku CAD, face artwork and sketch may be used, changed and shared
under the MIT license in LICENSE.txt. Third-party Arduino libraries retain
their own licenses. The guide uses the previously selected document template.
