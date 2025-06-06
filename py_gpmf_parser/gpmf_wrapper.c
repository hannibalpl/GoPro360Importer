#include <Python.h>
#include "GPMF_parser.h"
#include "GPMF_mp4reader.h"

static PyObject* open_mp4(PyObject* self, PyObject* args) {
    const char* filepath;
    if (!PyArg_ParseTuple(args, "s", &filepath)) return NULL;

    size_t mp4handle = OpenMP4Source(filepath);
    if (!mp4handle) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to open MP4");
        return NULL;
    }

    CloseSource(mp4handle);
    Py_RETURN_TRUE;
}

static PyMethodDef GPMFMethods[] = {
    {"open_mp4", open_mp4, METH_VARARGS, "Open MP4 and return handle."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef gpmfmodule = {
    PyModuleDef_HEAD_INIT,
    "gpmf_parser", NULL, -1, GPMFMethods
};

PyMODINIT_FUNC PyInit_gpmf_parser(void) {
    return PyModule_Create(&gpmfmodule);
}