{pkgs}: {
  deps = [
    pkgs.vulkan-loader
    pkgs.xorg.xorgserver
    pkgs.libGL
    pkgs.mesa
    pkgs.xorg.libXext
    pkgs.xorg.libX11
    pkgs.portmidi
    pkgs.pkg-config
    pkgs.libpng
    pkgs.libjpeg
    pkgs.freetype
    pkgs.fontconfig
    pkgs.SDL2_ttf
    pkgs.SDL2_mixer
    pkgs.SDL2_image
    pkgs.SDL2
  ];
}
