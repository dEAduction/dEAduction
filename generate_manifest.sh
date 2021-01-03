#cd src/deaduction/
#find share -type f > ../../MANIFEST.in
#sed -i 's/^/include /' ../../MANIFEST.in

find src/deaduction/share/ -type f > MANIFEST.in
sed -i 's/^/include /' MANIFEST.in
