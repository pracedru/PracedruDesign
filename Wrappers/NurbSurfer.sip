// Define the SIP wrapper to the hellosip library.

%Module NurbSurfer

%Import QtCore/QtCoremod.sip

class Nurbs {

%TypeHeaderCode
#include <nurbs.h>
%End

public:
    Nurbs(QObject *parent /TransferThis/ = nullptr);
    void setControls(QList<Vertex> controls);
    Vertex C(double u);
    QList<Vertex> range(int divisions);
};

